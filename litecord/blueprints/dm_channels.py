"""

Litecord
Copyright (C) 2018-2019  Luna Mendes

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

from quart import Blueprint, current_app as app, jsonify
from logbook import Logger

from litecord.blueprints.auth import token_check
from litecord.blueprints.checks import channel_check
from litecord.enums import ChannelType
from litecord.errors import BadRequest, Forbidden
from litecord.snowflake import get_snowflake

log = Logger(__name__)
bp = Blueprint('dm_channels', __name__)


async def _gdm_create(user_id, peer_id) -> int:
    """Create a group dm, given two users.

    Returns the new GDM id.
    """
    channel_id = get_snowflake()

    # TODO

    return channel_id


async def _gdm_add_recipient(channel_id: int, peer_id: int, *, user_id=None):
    """Add a recipient to a Group DM.

    Dispatches:
     - A system message with the join (depending of user_id)
     - A CHANNEL_CREATE to the peer.
     - A CHANNEL_UPDATE to all remaining recipients.
    """

    # TODO
    pass


async def _gdm_remove_recipient(channel_id: int, peer_id: int, *, user_id=None):
    """Remove a member from a GDM.

    Dispatches:
     - A system message with the leave or forced removal (depending if user_id)
        exists or not.
     - A CHANNEL_DELETE to the peer.
     - A CHANNEL_UPDATE to all remaining recipients.
    """

    # TODO
    pass


@bp.route('/<int:dm_chan>/receipients/<int:peer_id>', methods=['PUT'])
async def add_to_group_dm(dm_chan, peer_id):
    """Adds a member to a group dm OR creates a group dm."""
    user_id = await token_check()

    # other_id is the owner of the group dm (gdm) if the
    # given channel is a gdm

    # other_id is the peer of the dm if the given channel is a dm
    ctype, other_id = await channel_check(
        user_id, dm_chan,
        only=[ChannelType.DM, ChannelType.GROUP_DM]
    )

    # check relationship with the given user id
    # and the user id making the request
    friends = await app.user_storage.are_friends_with(user_id, peer_id)

    if not friends:
        raise BadRequest('Cant insert peer into dm')

    if ctype == ChannelType.DM:
        dm_chan = await _gdm_create(
            user_id, other_id
        )

    await _gdm_add_recipient(dm_chan, peer_id, user_id=user_id)

    return jsonify(
        await app.storage.get_channel(dm_chan)
    )


@bp.route('/<int:dm_chan>/recipients/<int:user_id>', methods=['DELETE'])
async def remove_from_group_dm(dm_chan, user_id):
    """Remove users from group dm."""
    user_id = await token_check()
    _ctype, owner_id = await channel_check(
        user_id, dm_chan, only=ChannelType.GROUP_DM
    )

    if owner_id != user_id:
        raise Forbidden('You are now the owner of the group DM')

    await _gdm_remove_recipient(dm_chan, user_id)
    return '', 204
