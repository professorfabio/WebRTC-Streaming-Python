from aiohttp import web

offer = None
answer = None
candidates_a = []
candidates_b = []

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

@routes.post("/candidate/a")
async def post_candidate_a(request):
    candidates_a.append(await request.text())
    return web.Response(text="OK")

@routes.get("/candidate/a")
async def get_candidate_a(request):
    return web.json_response(candidates_a)

@routes.post("/candidate/b")
async def post_candidate_b(request):
    candidates_b.append(await request.text())
    return web.Response(text="OK")

@routes.get("/candidate/b")
async def get_candidate_b(request):
    return web.json_response(candidates_b)

app = web.Application()
app.add_routes(routes)

web.run_app(app, port=8080)
