모킹
```
response = route.fetch()
print(f" 응답: {response.json()}")
route.fulfill(response=response)
```
모니터링
```
    page.on("request", lambda request: print(">>", request.method, request.url))
    page.on("response", lambda response: print("<<", response.status, response.url))
```