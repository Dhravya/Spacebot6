channel_map = {
    "message_updates": [
        "message_delete",
        "message_edit",
        "bulk_delete",
        "image_delete",
    ],
    "member_updates": [
        "member_join",
        "member_leave",
        "invite_info",
        "member_role_add",
        "member_role_remove",
        "nickname_change",
    ],
    "role_channel_updates": [
        "role_create",
        "role_delete",
        "role_update",
        "channel_create",
        "channel_delete",
        "channel_update",
        "voice_channel_join",
        "voice_channel_leave",
        "voice_channel_move",
    ],
    "guild_updates": ["guild_create", "guild_delete", "guild_update"],
    "moderation_updates": ["member_ban", "member_unban", "moderator_actions"],
}
