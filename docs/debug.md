모킹
```
response = route.fetch()
print(f" 응답: {response.json()}")
route.fulfill(response=response)
```
백엔드
```
    page.on("request", lambda req: print(f" {req.method} {req.url}"))
    page.on("response", lambda res: print(f" {res.status} {res.url}"))
```