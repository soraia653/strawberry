import pytest

from strawberry.channels.handlers.ws_handler import GraphQLWSConsumer
from strawberry.channels.testing import GraphQLWebsocketCommunicator
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from tests.views.schema import schema

application = GraphQLWSConsumer.as_asgi(schema=schema, keep_alive_interval=50)


@pytest.fixture(params=[GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL])
async def communicator(request):
    async with GraphQLWebsocketCommunicator(
        protocol=request.param, application=application, path="/graphql"
    ) as client:
        yield client


async def test_simple_subscribe(communicator):

    async for res in communicator.subscribe(
        query='subscription { echo(message: "Hi") }'
    ):
        assert res.data == {"echo": "Hi"}


async def test_subscribe_unexpected_error(communicator):
    async for res in communicator.subscribe(
        query='subscription { exception(message: "Hi") }'
    ):
        assert res.errors[0].message == "Hi"


async def test_graphql_error(communicator):
    async for res in communicator.subscribe(
        query='subscription { error(message: "Hi") }'
    ):
        assert res.errors[0].message == "Hi"
