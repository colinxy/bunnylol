
async def history_middleware_factory(app, handler):
    async def history_middleware(request):
        return await handler(request)

    return history_middleware


middleware_factories = [
    history_middleware_factory,
]
