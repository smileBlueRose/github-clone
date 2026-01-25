from infrastructure.di.container import Container

container = Container()

container.wire(modules=["infrastructure.middleware.auth"])
container.wire(modules=["api.v1.auth", "api.v1.git"])
