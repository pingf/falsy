# falsy
FAL.S.Y

### description
  it's a api framework.
  using falcon, swagger, yaml together!
  
### license
  MIT and Apache v2
  
### showtime

the transition animation is a little bit slow because of the record software

![ScreenShot](https://raw.githubusercontent.com/pingf/falsy/master/demo.gif)


### how to install it
  `pip install falsy`
  
### how to use it
1. writting the server code(main.py)
  ```python
    from falsy.falsy import FALSY

    f = FALSY(static_path='test', static_dir='static')   #you need create the dir called static before you run
    f.begin_api()
    f.swagger('test.yml', ui=True,theme='impress') #impress theme is the responsive swagger ui, or you can use 'normal' here
    f.end_api()
    api = f.api
  ```
2. writting the yml file
  ```
  swagger: '2.0'
  info:
    title: FALSY SIMPLE DEMO API
    version: "0.1"
  consumes:
    - application/json
  produces:
    - application/json
  basePath: "/v1"
  paths:
    '/hello':
      get:
        tags: [Method]
        operationId: demo.get_it
        summary: testing
        parameters:
          - name: name
            in: query
            type: string
            default: 'john'
        responses:
          200:
            description: Return response
  ```
  
3. writting the operation handler(demo.py)
  ```python
  def get_it(name):
    return {
        'name': name
    }
  ```
  
4. run it
  `gunicorn -b 0.0.0.0:8001 main:api --reload -w 1 --threads 1`
  
5. visit the ui page
  `http://0.0.0.0:8001/v1/ui/`
  make sure it ends with '/'
  
### video demo

![ScreenShot](https://raw.githubusercontent.com/pingf/falsy/master/falsy.gif)
  
