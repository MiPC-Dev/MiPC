from MiPC import StreamingClient

class Stream(StreamingClient):
    
    async def on_note(self, ctx):
        print("[" + ctx.author.name + "(@" + ctx.author.username + ")" + "] " + ctx.text)
        
    async def on_ready():
        print("ready")
        
mibot = Stream("server", "token")
mibot.run()