import websocket
import threading
import traceback
import random
import redis
import time
import json
import rel

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

import sys
sys.stdout = Unbuffered(sys.stdout)

r = redis.Redis(host='redis', decode_responses=True)

class DiscordUser():
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.username = data["username"]
        self.discriminator = data["discriminator"]
        self.global_name = data["global_name"]
        self.avatar = data["avatar"]
        self.bot = data["bot"] if "bot" in data else None
        self.system = data["system"] if "system" in data else None
        self.mfa_enabled = data["mfa_enabled"] if "mfa_enabled" in data else None
        self.banner = data["banner"] if "banner" in data else None
        self.accent_color = data["accent_color"] if "accent_color" in data else None
        self.locale = data["locale"] if "locale" in data else None
        self.verified = data["verified"] if "verified" in data else None
        self.email = data["email"] if "email" in data else None
        self.flags = data["flags"] if "flags" in data else None
        self.premium_type = data["premium_type"] if "premium_type" in data else None
        self.public_flags = data["public_flags"] if "public_flags" in data else None
        self.avatar_decoration = data["avatar_decoration"] if "avatar_decoration" in data else None
    
    def __repr__(self) -> str:
        return f"DiscordUser(id={self.id}, username={self.username}, discriminator={self.discriminator}, global_name={self.global_name}, avatar={self.avatar}, bot={self.bot}, system={self.system}, mfa_enabled={self.mfa_enabled}, banner={self.banner}, accent_color={self.accent_color}, locale={self.locale}, verified={self.verified}, email={self.email}, flags={self.flags}, premium_type={self.premium_type}, public_flags={self.public_flags}, avatar_decoration={self.avatar_decoration})"


class DiscordMember():
    def __init__(self, data):
        self.data = data
        self.user = DiscordUser(data["user"]) if "user" in data else None
        self.nick = data["nick"] if "nick" in data else None
        self.roles = data["roles"]
        self.joined_at = data["joined_at"]
        self.premium_since = data["premium_since"] if "premium_since" in data else None
        self.deaf = data["deaf"]
        self.mute = data["mute"]
        self.flags = data["flags"]
        self.pending = data["pending"] if "pending" in data else None
        self.permissions = data["permissions"] if "permissions" in data else None
        self.communication_disabled_until = data["communication_disabled_until"] if "communication_disabled_until" in data else None
    
    def __repr__(self) -> str:
        return f"DiscordMember(user={self.user}, nick={self.nick}, roles={self.roles}, joined_at={self.joined_at}, premium_since={self.premium_since}, deaf={self.deaf}, mute={self.mute}, flags={self.flags}, pending={self.pending}, permissions={self.permissions}, communication_disabled_until={self.communication_disabled_until})"

class ArrayOf():
    def __init__(self, data, theType):
        self.data = data
        self.theType = theType
        self.objects = []
        for item in data:
            self.objects.append(theType(item))
    
    def __repr__(self) -> str:
        return f"ArrayOf(objects={self.objects}, {self.theType})"

class ChannelMention():
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.guild_id = data["guild_id"]
        self.type = data["type"]
        self.name = data["name"]

    def __repr__(self) -> str:
        return f"ChannelMention(id={self.id}, guild_id={self.guild_id}, type={self.type}, name={self.name})"

class Attachment():
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.filename = data["filename"]
        self.description = data["description"] if "description" in data else None
        self.content_type = data["content_type"] if "content_type" in data else None
        self.size = data["size"]
        self.url = data["url"]
        self.proxy_url = data["proxy_url"]
        self.height = data["height"] if "height" in data else None
        self.width = data["width"] if "width" in data else None
        self.ephemeral = data["ephemeral"] if "ephemeral" in data else None
        self.duration_secs = data["duration_secs"] if "duration_secs" in data else None
        self.waveform = data["waveform"] if "waveform" in data else None
        self.flags = data["flags"] if "flags" in data else None
    
    def __repr__(self) -> str:
        return f"Attachment(id={self.id}, filename={self.filename}, description={self.description}, content_type={self.content_type}, size={self.size}, url={self.url}, proxy_url={self.proxy_url}, height={self.height}, width={self.width}, ephemeral={self.ephemeral}, duration_secs={self.duration_secs}, waveform={self.waveform}, flags={self.flags})"

class EmbedFooter():
    def __init__(self, data):
        self.data = data
        self.text = data["text"]
        self.icon_url = data["icon_url"] if "icon_url" in data else None
        self.proxy_icon_url = data["proxy_icon_url"] if "proxy_icon_url" in data else None
    
    def __repr__(self) -> str:
        return f"EmbedFooter(text={self.text}, icon_url={self.icon_url}, proxy_icon_url={self.proxy_icon_url})"

class EmbedImage():
    def __init__(self, data):
        self.data = data
        self.url = data["url"]
        self.proxy_url = data["proxy_url"] if "proxy_url" in data else None
        self.height = data["height"] if "height" in data else None
        self.width = data["width"] if "width" in data else None
    
    def __repr__(self) -> str:
        return f"EmbedImage(url={self.url}, proxy_url={self.proxy_url}, height={self.height}, width={self.width})"

class EmbedThumbnail():
    def __init__(self, data):
        self.data = data
        self.url = data["url"]
        self.proxy_url = data["proxy_url"] if "proxy_url" in data else None
        self.height = data["height"] if "height" in data else None
        self.width = data["width"] if "width" in data else None
    
    def __repr__(self) -> str:
        return f"EmbedThumbnail(url={self.url}, proxy_url={self.proxy_url}, height={self.height}, width={self.width})"

class EmbedVideo():
    def __init__(self, data):
        self.data = data
        self.url = data["url"] if "url" in data else None
        self.proxy_url = data["proxy_url"] if "proxy_url" in data else None
        self.height = data["height"] if "height" in data else None
        self.width = data["width"] if "width" in data else None
    
    def __repr__(self) -> str:
        return f"EmbedVideo(url={self.url}, proxy_url={self.proxy_url}, height={self.height}, width={self.width})"

class EmbedProvider():
    def __init__(self, data):
        self.data = data
        self.name = data["name"] if "name" in data else None
        self.url = data["url"] if "url" in data else None
    
    def __repr__(self) -> str:
        return f"EmbedProvider(name={self.name}, url={self.url})"

class EmbedAuthor():
    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.url = data["url"] if "url" in data else None
        self.icon_url = data["icon_url"] if "icon_url" in data else None
        self.proxy_icon_url = data["proxy_icon_url"] if "proxy_icon_url" in data else None
    
    def __repr__(self) -> str:
        return f"EmbedAuthor(name={self.name}, url={self.url}, icon_url={self.icon_url}, proxy_icon_url={self.proxy_icon_url})"

class EmbedField():
    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.value = data["value"]
        self.inline = data["inline"] if "inline" in data else None
    
    def __repr__(self) -> str:
        return f"EmbedField(name={self.name}, value={self.value}, inline={self.inline})"

class Embed():
    def __init__(self, data):
        self.data = data
        self.title = data["title"] if "title" in data else None
        self.type = data["type"] if "type" in data else None
        self.description = data["description"] if "description" in data else None
        self.url = data["url"] if "url" in data else None
        self.timestamp = data["timestamp"] if "timestamp" in data else None
        self.color = data["color"] if "color" in data else None
        self.footer = EmbedFooter(data["footer"]) if "footer" in data else None
        self.image = EmbedImage(data["image"]) if "image" in data else None
        self.thumbnail = EmbedThumbnail(data["thumbnail"]) if "thumbnail" in data else None
        self.video = EmbedVideo(data["video"]) if "video" in data else None
        self.provider = EmbedProvider(data["provider"]) if "provider" in data else None
        self.author = EmbedAuthor(data["author"]) if "author" in data else None
        self.fields = ArrayOf(data["fields"], EmbedField) if "fields" in data else None
    
    def __repr__(self) -> str:
        return f"Embed(title={self.title}, type={self.type}, description={self.description}, url={self.url}, timestamp={self.timestamp}, color={self.color}, footer={self.footer}, image={self.image}, thumbnail={self.thumbnail}, video={self.video}, provider={self.provider}, author={self.author}, fields={self.fields})"

class ReactionCountDetails():
    def __init__(self, data):
        self.data = data
        self.burst = data["burst"]
        self.normal = data["normal"]
    
    def __repr__(self) -> str:
        return f"ReactionCountDetails(burst={self.burst}, normal={self.normal})"

class Emoji():
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.name = data["name"]
        self.roles = data["roles"] if "roles" in data else None
        self.user = DiscordUser(data["user"]) if "user" in data else None
        self.require_colons = data["require_colons"] if "require_colons" in data else None
        self.managed = data["managed"] if "managed" in data else None
        self.animated = data["animated"] if "animated" in data else None
        self.available = data["available"] if "available" in data else None
    
    def __repr__(self) -> str:
        return f"Emoji(id={self.id}, name={self.name}, roles={self.roles}, user={self.user}, require_colons={self.require_colons}, managed={self.managed}, animated={self.animated}, available={self.available})"

class Reaction():
    def __init__(self, data):
        self.data = data
        self.count = data["count"]
        self.count_details = ReactionCountDetails(data["count_details"])
        self.me = data["me"]
        self.me_burst = data["me_burst"]
        self.emoji = Emoji(data["emoji"])
        self.burst_colors = data["burst_colors"]
    
    def __repr__(self) -> str:
        return f"Reaction(count={self.count}, count_details={self.count_details}, me={self.me}, me_burst={self.me_burst}, emoji={self.emoji}, burst_colors={self.burst_colors})"

class MessageActivity():
    JOIN = 1
    SPECTATE = 2
    LISTEN = 3
    JOIN_REQUEST = 5

    def __init__(self, data):
        self.data = data
        self.type = data["type"]
        self.party_id = data["party_id"] if "party_id" in data else None
    
    def __repr__(self) -> str:
        return f"MessageActivity(type={self.type}, party_id={self.party_id})"

class TeamMember():
    def __init__(self, data):
        self.data = data
        self.membership_state = data["membership_state"]
        self.team_id = data["team_id"]
        self.user = DiscordUser(data["user"])
        self.role = data["role"]
    
    def __repr__(self) -> str:
        return f"TeamMember(membership_state={self.membership_state}, team_id={self.team_id}, user={self.user}, role={self.role})"

class Team():
    def __init__(self, data):
        self.data = data
        self.icon = data["icon"]
        self.id = data["id"]
        self.members = ArrayOf(data["members"], TeamMember)
        self.name = data["name"]
        self.owner_user_id = data["owner_user_id"]
    
    def __repr__(self) -> str:
        return f"Team(icon={self.icon}, id={self.id}, members={self.members}, name={self.name}, owner_user_id={self.owner_user_id})"

class RoleTag():
    def __init__(self, data):
        self.data = data
        self.bot_id = data["bot_id"] if "bot_id" in data else None
        self.integration_id = data["integration_id"] if "integration_id" in data else None
        self.premium_subscriber = data["premium_subscriber"] if "premium_subscriber" in data else None
        self.subscription_listing_id = data["subscription_listing_id"] if "subscription_listing_id" in data else None
        self.available_for_purchase = data["available_for_purchase"] if "available_for_purchase" in data else None
        self.guild_connections = data["guild_connections"] if "guild_connections" in data else None
    
    def __repr__(self) -> str:
        return f"RoleTag(bot_id={self.bot_id}, integration_id={self.integration_id}, premium_subscriber={self.premium_subscriber}, subscription_listing_id={self.subscription_listing_id}, available_for_purchase={self.available_for_purchase}, guild_connections={self.guild_connections})"

class Role():
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.name = data["name"]
        self.color = data["color"]
        self.hoist = data["hoist"]
        self.icon = data["icon"] if "icon" in data else None
        self.unicode_emoji = data["unicode_emoji"] if "unicode_emoji" in data else None
        self.position = data["position"]
        self.permissions = data["permissions"]
        self.managed = data["managed"]
        self.mentionable = data["mentionable"]
        self.tags = ArrayOf(data["tags"], RoleTag) if "tags" in data else None
        self.flags = data["flags"]
    
    def __repr__(self) -> str:
        return f"Role(id={self.id}, name={self.name}, color={self.color}, hoist={self.hoist}, icon={self.icon}, unicode_emoji={self.unicode_emoji}, position={self.position}, permissions={self.permissions}, managed={self.managed}, mentionable={self.mentionable}, tags={self.tags}, flags={self.flags})"

class WelcomeScreenChannel():
    def __init__(self, data):
        self.data = data
        self.channel_id = data["channel_id"]
        self.description = data["description"]
        self.emoji_id = data["emoji_id"]
        self.emoji_name = data["emoji_name"]
    
    def __repr__(self) -> str:
        return f"WelcomeScreenChannel(channel_id={self.channel_id}, description={self.description}, emoji_id={self.emoji_id}, emoji_name={self.emoji_name})"

class WelcomeScreen():
    def __init__(self, data):
        self.data = data
        self.description = data["description"]
        self.welcome_channels = ArrayOf(data["welcome_channels"], WelcomeScreenChannel)
    
    def __repr__(self) -> str:
        return f"WelcomeScreen(description={self.description}, welcome_channels={self.welcome_channels})"

class Sticker():
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.pack_id = data["pack_id"] if "pack_id" in data else None
        self.name = data["name"]
        self.description = data["description"]
        self.tags = data["tags"]
        self.asset = data["asset"] if "asset" in data else None
        self.type = data["type"]
        self.format_type = data["format_type"]
        self.available = data["available"] if "available" in data else None
        self.guild_id = data["guild_id"] if "guild_id" in data else None
        self.user = DiscordUser(data["user"]) if "user" in data else None
        self.sort_value = data["sort_value"] if "sort_value" in data else None
    
    def __repr__(self) -> str:
        return f"Sticker(id={self.id}, pack_id={self.pack_id}, name={self.name}, description={self.description}, tags={self.tags}, asset={self.asset}, type={self.type}, format_type={self.format_type}, available={self.available}, guild_id={self.guild_id}, user={self.user}, sort_value={self.sort_value})"

class Guild():
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.name = data["name"]
        self.icon = data["icon"]
        self.icon_hash = data["icon_hash"] if "icon_hash" in data else None
        self.splash = data["splash"]
        self.discovery_splash = data["discovery_splash"]
        self.owner = data["owner"] if "owner" in data else None
        self.owner_id = data["owner_id"]
        self.permissions = data["permissions"] if "permissions" in data else None
        self.region = data["region"] if "region" in data else None
        self.afk_channel_id = data["afk_channel_id"]
        self.afk_timeout = data["afk_timeout"]
        self.widget_enabled = data["widget_enabled"] if "widget_enabled" in data else None
        self.widget_channel_id = data["widget_channel_id"] if "widget_channel_id" in data else None
        self.verification_level = data["verification_level"]
        self.default_message_notifications = data["default_message_notifications"]
        self.explicit_content_filter = data["explicit_content_filter"]
        self.roles = ArrayOf(data["roles"], Role)
        self.emojis = ArrayOf(data["emojis"], Emoji)
        self.features = data["features"]
        self.mfa_level = data["mfa_level"]
        self.application_id = data["application_id"]
        self.system_channel_id = data["system_channel_id"]
        self.system_channel_flags = data["system_channel_flags"]
        self.rules_channel_id = data["rules_channel_id"]
        self.max_presences = data["max_presences"] if "max_presences" in data else None
        self.max_members = data["max_members"] if "max_members" in data else None
        self.vanity_url_code = data["vanity_url_code"]
        self.description = data["description"]
        self.banner = data["banner"]
        self.premium_tier = data["premium_tier"]
        self.premium_subscription_count = data["premium_subscription_count"] if "premium_subscription_count" in data else None
        self.preferred_locale = data["preferred_locale"]
        self.public_updates_channel_id = data["public_updates_channel_id"]
        self.max_video_channel_users = data["max_video_channel_users"] if "max_video_channel_users" in data else None
        self.max_stage_video_channel_users = data["max_stage_video_channel_users"] if "max_stage_video_channel_users" in data else None
        self.approximate_member_count = data["approximate_member_count"] if "approximate_member_count" in data else None
        self.approximate_presence_count = data["approximate_presence_count"] if "approximate_presence_count" in data else None
        self.welcome_screen = WelcomeScreen(data["welcome_screen"]) if "welcome_screen" in data else None
        self.nsfw_level = data["nsfw_level"]
        self.stickers = ArrayOf(data["stickers"], Sticker)
        self.premium_progress_bar_enabled = data["premium_progress_bar_enabled"]
        self.safety_alerts_channel_id = data["safety_alerts_channel_id"]
    
    def __repr__(self) -> str:
        return f"Guild(id={self.id}, name={self.name}, icon={self.icon}, icon_hash={self.icon_hash}, splash={self.splash}, discovery_splash={self.discovery_splash}, owner={self.owner}, owner_id={self.owner_id}, permissions={self.permissions}, region={self.region}, afk_channel_id={self.afk_channel_id}, afk_timeout={self.afk_timeout}, widget_enabled={self.widget_enabled}, widget_channel_id={self.widget_channel_id}, verification_level={self.verification_level}, default_message_notifications={self.default_message_notifications}, explicit_content_filter={self.explicit_content_filter}, roles={self.roles}, emojis={self.emojis}, features={self.features}, mfa_level={self.mfa_level}, application_id={self.application_id}, system_channel_id={self.system_channel_id}, system_channel_flags={self.system_channel_flags}, rules_channel_id={self.rules_channel_id}, max_presences={self.max_presences}, max_members={self.max_members}, vanity_url_code={self.vanity_url_code}, description={self.description}, banner={self.banner}, premium_tier={self.premium_tier}, premium_subscription_count={self.premium_subscription_count}, preferred_locale={self.preferred_locale}, public_updates_channel_id={self.public_updates_channel_id}, max_video_channel_users={self.max_video_channel_users}, max_stage_video_channel_users={self.max_stage_video_channel_users}, approximate_member_count={self.approximate_member_count}, approximate_presence_count={self.approximate_presence_count}, welcome_screen={self.welcome_screen}, nsfw_level={self.nsfw_level}, stickers={self.stickers}, premium_progress_bar_enabled={self.premium_progress_bar_enabled}, safety_alerts_channel_id={self.safety_alerts_channel_id})"

class InstallParams():
    def __init__(self, data):
        self.data = data
        self.scopes = data["scopes"]
        self.permissions = data["permissions"]
    
    def __repr__(self) -> str:
        return f"InstallParams(scopes={self.scopes}, permissions={self.permissions})"

class Application():
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.name = data["name"]
        self.description = data["description"]
        self.rpc_origins = data["rpc_origins"] if "rpc_origins" in data else None
        self.bot_public = data["bot_public"]
        self.bot_require_code_grant = data["bot_require_code_grant"]
        self.bot = DiscordUser(data["bot"]) if "bot" in data else None
        self.terms_of_service_url = data["terms_of_service_url"] if "terms_of_service_url" in data else None
        self.privacy_policy_url = data["privacy_policy_url"] if "privacy_policy_url" in data else None
        self.owner = DiscordUser(data["owner"]) if "owner" in data else None
        self.summary = data["summary"] if "summary" in data else None
        self.verify_key = data["verify_key"]
        self.team = Team(data["team"]) if data["team"] is not None else None
        self.guild_id = data["guild_id"] if "guild_id" in data else None
        self.guild = Guild(data["guild"]) if "guild" in data else None
        self.primary_sku_id = data["primary_sku_id"] if "primary_sku_id" in data else None
        self.slug = data["slug"] if "slug" in data else None
        self.cover_image = data["cover_image"] if "cover_image" in data else None
        self.flags = data["flags"] if "flags" in data else None
        self.approximate_guild_count = data["approximate_guild_count"] if "approximate_guild_count" in data else None
        self.interactions_endpoint_url = data["interactions_endpoint_url"] if "interactions_endpoint_url" in data else None
        self.role_connections_verification_url = data["role_connections_verification_url"] if "role_connections_verification_url" in data else None
        self.tags = data["tags"] if "tags" in data else None
        self.install_params = InstallParams(data["install_params"]) if "install_params" in data else None
        self.custom_install_url = data["custom_install_url"] if "custom_install_url" in data else None
    
    def __repr__(self) -> str:
        return f"Application(id={self.id}, name={self.name}, description={self.description}, rpc_origins={self.rpc_origins}, bot_public={self.bot_public}, bot_require_code_grant={self.bot_require_code_grant}, bot={self.bot}, terms_of_service_url={self.terms_of_service_url}, privacy_policy_url={self.privacy_policy_url}, owner={self.owner}, summary={self.summary}, verify_key={self.verify_key}, team={self.team}, guild_id={self.guild_id}, guild={self.guild}, primary_sku_id={self.primary_sku_id}, slug={self.slug}, cover_image={self.cover_image}, flags={self.flags}, approximate_guild_count={self.approximate_guild_count}, interactions_endpoint_url={self.interactions_endpoint_url}, role_connections_verification_url={self.role_connections_verification_url}, tags={self.tags}, install_params={self.install_params}, custom_install_url={self.custom_install_url})"

class MessageReference():
    def __init__(self, data):
        self.data = data
        self.message_id = data["message_id"] if "message_id" in data else None
        self.channel_id = data["channel_id"] if "channel_id" in data else None
        self.guild_id = data["guild_id"] if "guild_id" in data else None
        self.fail_if_not_exists = data["fail_if_not_exists"] if "fail_if_not_exists" in data else None
    
    def __repr__(self) -> str:
        return f"MessageReference(message_id={self.message_id}, channel_id={self.channel_id}, guild_id={self.guild_id}, fail_if_not_exists={self.fail_if_not_exists})"

class MessageInteraction():
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.type = data["type"]
        self.name = data["name"]
        self.user = DiscordUser(data["user"])
        self.member = DiscordMember(data["member"]) if "member" in data else None
    
    def __repr__(self) -> str:
        return f"MessageInteraction(id={self.id}, type={self.type}, name={self.name}, user={self.user}, member={self.member})"

class ThreadMetadata():
    def __init__(self, data):
        self.data = data
        self.archived = data["archived"]
        self.auto_archive_duration = data["auto_archive_duration"]
        self.archive_timestamp = data["archive_timestamp"]
        self.locked = data["locked"]
        self.invitable = data["invitable"] if "invitable" in data else None
        self.create_timestamp = data["create_timestamp"] if "create_timestamp" in data else None
    
    def __repr__(self) -> str:
        return f"ThreadMetadata(archived={self.archived}, auto_archive_duration={self.auto_archive_duration}, archive_timestamp={self.archive_timestamp}, locked={self.locked}, invitable={self.invitable}, create_timestamp={self.create_timestamp})"

class Tag():
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.name = data["name"]
        self.moderated = data["moderated"]
        self.emoji_id = data["emoji_id"]
        self.emoji_name = data["emoji_name"]
    
    def __repr__(self) -> str:
        return f"Tag(id={self.id}, name={self.name}, moderated={self.moderated}, emoji_id={self.emoji_id}, emoji_name={self.emoji_name})"

class DefaultReaction():
    def __init__(self, data):
        self.data = data
        self.emoji_id = data["emoji_id"] if "emoji_id" in data else None
        self.emoji_name = data["emoji_name"]
    
    def __repr__(self) -> str:
        return f"DefaultReaction(emoji_id={self.emoji_id}, emoji_name={self.emoji_name})"

class Channel():
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.type = data["type"]
        self.guild_id = data["guild_id"] if "guild_id" in data else None
        self.position = data["position"] if "position" in data else None
        self.permission_overwrites = data["permission_overwrites"] if "permission_overwrites" in data else None
        self.name = data["name"] if "name" in data else None
        self.topic = data["topic"] if "topic" in data else None
        self.nsfw = data["nsfw"] if "nsfw" in data else None
        self.last_message_id = data["last_message_id"] if "last_message_id" in data else None
        self.bitrate = data["bitrate"] if "bitrate" in data else None
        self.user_limit = data["user_limit"] if "user_limit" in data else None
        self.rate_limit_per_user = data["rate_limit_per_user"] if "rate_limit_per_user" in data else None
        self.recipients = ArrayOf(data["recipients"], DiscordUser) if "recipients" in data else None
        self.icon = data["icon"] if "icon" in data else None
        self.owner_id = data["owner_id"] if "owner_id" in data else None
        self.application_id = data["application_id"] if "application_id" in data else None
        self.managed = data["managed"] if "managed" in data else None
        self.parent_id = data["parent_id"] if "parent_id" in data else None
        self.last_pin_timestamp = data["last_pin_timestamp"] if "last_pin_timestamp" in data else None
        self.rtc_region = data["rtc_region"] if "rtc_region" in data else None
        self.video_quality_mode = data["video_quality_mode"] if "video_quality_mode" in data else None
        self.message_count = data["message_count"] if "message_count" in data else None
        self.member_count = data["member_count"] if "member_count" in data else None
        self.thread_metadata = ThreadMetadata(data["thread_metadata"]) if "thread_metadata" in data else None
        self.member = DiscordMember(data["member"]) if "member" in data else None
        self.default_auto_archive_duration = data["default_auto_archive_duration"] if "default_auto_archive_duration" in data else None
        self.permissions = data["permissions"] if "permissions" in data else None
        self.flags = data["flags"] if "flags" in data else None
        self.total_message_sent = data["total_message_sent"] if "total_message_sent" in data else None
        self.available_tags = ArrayOf(data["available_tags"], Tag) if "available_tags" in data else None
        self.applied_tags = ArrayOf(data["applied_tags"], Tag) if "applied_tags" in data else None
        self.default_reaction_emoji = DefaultReaction(data["default_reaction_emoji"]) if "default_reaction_emoji" in data else None
        self.default_thread_rate_limit_per_user = data["default_thread_rate_limit_per_user"] if "default_thread_rate_limit_per_user" in data else None
        self.default_sort_order = data["default_sort_order"] if "default_sort_order" in data else None
        self.default_forum_layout = data["default_forum_layout"] if "default_forum_layout" in data else None
    
    def __repr__(self) -> str:
        return f"Channel(id={self.id}, type={self.type}, guild_id={self.guild_id}, position={self.position}, permission_overwrites={self.permission_overwrites}, name={self.name}, topic={self.topic}, nsfw={self.nsfw}, last_message_id={self.last_message_id}, bitrate={self.bitrate}, user_limit={self.user_limit}, rate_limit_per_user={self.rate_limit_per_user}, recipients={self.recipients}, icon={self.icon}, owner_id={self.owner_id}, application_id={self.application_id}, managed={self.managed}, parent_id={self.parent_id}, last_pin_timestamp={self.last_pin_timestamp}, rtc_region={self.rtc_region}, video_quality_mode={self.video_quality_mode}, message_count={self.message_count}, member_count={self.member_count}, thread_metadata={self.thread_metadata}, member={self.member}, default_auto_archive_duration={self.default_auto_archive_duration}, permissions={self.permissions}, flags={self.flags}, total_message_sent={self.total_message_sent}, available_tags={self.available_tags}, applied_tags={self.applied_tags}, default_reaction_emoji={self.default_reaction_emoji}, default_thread_rate_limit_per_user={self.default_thread_rate_limit_per_user}, default_sort_order={self.default_sort_order}, default_forum_layout={self.default_forum_layout})"

class RoleSubscriptionData():
    def __init__(self, data):
        self.data = data
        self.role_subscription_listing_id = data["role_subscription_listing_id"]
        self.tier_name = data["tier_name"]
        self.total_months_subscribed = data["total_months_subscribed"]
        self.is_renewal = data["is_renewal"]
    
    def __repr__(self) -> str:
        return f"RoleSubscriptionData(role_subscription_listing_id={self.role_subscription_listing_id}, tier_name={self.tier_name}, total_months_subscribed={self.total_months_subscribed}, is_renewal={self.is_renewal})"

class Resolved():
    def __init__(self, data):
        self.data = data
        self.members = data["members"] if "members" in data else None
        self.users = data["users"] if "users" in data else None
        self.roles = data["roles"] if "roles" in data else None
        self.channels = data["channels"] if "channels" in data else None
        self.messages = data["messages"] if "messages" in data else None
        self.attachments = data["attachments"] if "attachments" in data else None
    
    def __repr__(self) -> str:
        return f"Resolved(members={self.members}, users={self.users}, roles={self.roles}, channels={self.channels}, messages={self.messages}, attachments={self.attachments})"

class MessageObject():
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.channel_id = data["channel_id"]
        self.author = DiscordUser(data["author"])
        self.content = data["content"]
        self.timestamp = data["timestamp"]
        self.edited_timestamp = data["edited_timestamp"]
        self.tts = data["tts"]
        self.mention_everyone = data["mention_everyone"]
        self.mentions = ArrayOf(data["mentions"], DiscordUser)
        self.mention_roles = data["mention_roles"]
        self.mention_channels = ArrayOf(data["mention_channels"], ChannelMention) if "mention_channels" in data else None
        self.attachments = ArrayOf(data["attachments"], Attachment)
        self.embeds = ArrayOf(data["embeds"], Embed)
        self.reactions = ArrayOf(data["reactions"], Reaction) if "reactions" in data else None
        self.nonce = data["nonce"] if "nonce" in data else None
        self.pinned = data["pinned"]
        self.webhook_id = data["webhook_id"] if "webhook_id" in data else None
        self.type = data["type"]
        self.activity = MessageActivity(data["activity"]) if "activity" in data else None
        self.application = Application(data["application"]) if "application" in data else None
        self.application_id = data["application_id"] if "application_id" in data else None
        self.message_reference = MessageReference(data["message_reference"]) if "message_reference" in data else None
        self.flags = data["flags"] if "flags" in data else None
        self.referenced_message = MessageObject(data["referenced_message"]) if "referenced_message" in data and data["referenced_message"] is not None else None # Fuck this 
        self.interaction = MessageInteraction(data["interaction"]) if "interaction" in data else None
        self.thread = Channel(data["thread"]) if "thread" in data else None
        self.components = data["components"] if "components" in data else None # TODO: Implement components
        self.sticker_items = data["sticker_items"] if "sticker_items" in data else None
        self.stickers = ArrayOf(data["stickers"], Sticker) if "stickers" in data else None
        self.position = data["position"] if "position" in data else None
        self.role_subscription_data = RoleSubscriptionData(data["role_subscription_data"]) if "role_subscription_data" in data else None
        self.resolved = Resolved(data["resolved"]) if "resolved" in data else None # TODO: May break stuff
    
    def __repr__(self):
        return f"MessageObject(id={self.id}, channel_id={self.channel_id}, author={self.author}, content={self.content}, timestamp={self.timestamp}, edited_timestamp={self.edited_timestamp}, tts={self.tts}, mention_everyone={self.mention_everyone}, mentions={self.mentions}, mention_roles={self.mention_roles}, mention_channels={self.mention_channels}, attachments={self.attachments}, embeds={self.embeds}, reactions={self.reactions}, nonce={self.nonce}, pinned={self.pinned}, webhook_id={self.webhook_id}, type={self.type}, activity={self.activity}, application={self.application}, application_id={self.application_id}, message_reference={self.message_reference}, flags={self.flags}, referenced_message={self.referenced_message}, interaction={self.interaction}, thread={self.thread}, components={self.components}, sticker_items={self.sticker_items}, stickers={self.stickers}, position={self.position}, role_subscription_data={self.role_subscription_data}, resolved={self.resolved})"

class DiscordGatewayMessageCreate(MessageObject):
    def __init__(self, data):
        self.guild_id = data["guild_id"] if "guild_id" in data else None
        self.member = DiscordMember(data["member"]) if "member" in data else None
        self.mentions = ArrayOf(data["mentions"], DiscordUser)
        super().__init__(data)
    
    def __repr__(self):
        return f"DiscordGatewayMessageCreate(id={self.id}, channel_id={self.channel_id}, author={self.author}, content={self.content}, timestamp={self.timestamp}, edited_timestamp={self.edited_timestamp}, tts={self.tts}, mention_everyone={self.mention_everyone}, mentions={self.mentions}, mention_roles={self.mention_roles}, mention_channels={self.mention_channels}, attachments={self.attachments}, embeds={self.embeds}, reactions={self.reactions}, nonce={self.nonce}, pinned={self.pinned}, webhook_id={self.webhook_id}, type={self.type}, activity={self.activity}, application={self.application}, application_id={self.application_id}, message_reference={self.message_reference}, flags={self.flags}, referenced_message={self.referenced_message}, interaction={self.interaction}, thread={self.thread}, components={self.components}, sticker_items={self.sticker_items}, stickers={self.stickers}, position={self.position}, role_subscription_data={self.role_subscription_data}, resolved={self.resolved}, guild_id={self.guild_id}, member={self.member})"

def heartbeat(ws, interval):
    time.sleep(interval * random.random())
    while True:
        ws.send(json.dumps({"op": 1, "d": None}))
        print("Sent heartbeat")
        time.sleep(interval)

def on_message(ws, message):
    msg = json.loads(message)
    if msg["op"] == 10:
        print("Received HELLO")
        heartbeat_interval = msg["d"]["heartbeat_interval"] / 1000
        print("Heartbeat interval: " + str(heartbeat_interval) + " seconds")
        threading.Thread(
            target=heartbeat,
            args=(ws, heartbeat_interval),
            daemon=True
        ).start()

    if msg["t"] == "MESSAGE_CREATE":
        print("received something")
        message_create = DiscordGatewayMessageCreate(msg["d"])
        print(f"Received message: {message_create}")

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection and sent HELLO")
    helo = json.load(open("data/helo.json"))
    ws.send(json.dumps(helo))

def ws_on_error(ws, error):
    raise error

if __name__ == "__main__":
    ws = websocket.WebSocketApp("wss://gateway.discord.gg/?encoding=json",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=ws_on_error,
                              on_close=on_close)
    

    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()