from aiohttp import web

offer = None
answer = None

routes = web.RouteTableDef()

@routes.post("/offer")
async def post_offer(request):
    global offer
    offer = await request.text()
    return web.Response(text="OK")

@routes.get("/offer")
async def get_offer(request):
    return web.Response(text=offer or "")

@routes.post("/answer")
async def post_answer(request):
    global answer
    answer = await request.text()
    return web.Response(text="OK")

@routes.get("/answer")
async def get_answer(request):
    return web.Response(text=answer or "")

app = web.Application()
app.add_routes(routes)

web.run_app(app, port=8080)
