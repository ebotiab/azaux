# import pytest
# from unittest.mock import AsyncMock, MagicMock
# from azaux.queue_manager import QueueManager


# @pytest.mark.asyncio
# async def test_send_messages(queue_manager: QueueManager):
#     # Mock the send_message method of the queue client
#     queue_client = queue_manager.get_client.return_value
#     queue_client.send_message = AsyncMock()

#     # Define the input messages
#     instance_inputs = ["message1", "message2", "message3"]

#     # Call the send_messages method of QueueManager
#     await queue_manager.send_messages(instance_inputs)

#     # Check if the send_message method of the queue client was called with the correct arguments
#     send_message_calls = [call[0][0] for call in queue_client.send_message.call_args_list]
#     assert send_message_calls == instance_inputs