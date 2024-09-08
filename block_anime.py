from mitmproxy import http

def request(flow: http.HTTPFlow) -> None:
    pass

def response(flow: http.HTTPFlow) -> None:

        assert(flow.response)
        assert(flow.response.content)
    
        new_content = flow.response.content.lower().replace(b"anime", b"chess")
        
        flow.response.content = new_content
        domain = flow.request.pretty_host

        print(f"Modified response for domain: {domain}")
