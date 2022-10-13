# Philo-Coding-Assessment

This is an implementation of a TCP Server that manages a LIFO stack using 
[Twisted](https://docs.twisted.org/en/twisted-18.7.0/core/howto/servers.html), a platform for developing internet applications.

## Requirements 
Note: Docker desktop installation [here](https://docs.docker.com/get-docker/)
```
Docker Desktop
```

## Run
```
docker-compose run -p 8080:8080 tcp_server
```

## Test
Note: Ruby 2.3.0 or greater is required
```
ruby tests/stack-test.rb -v 
python tests/server-tests.py TestStackServer
```

