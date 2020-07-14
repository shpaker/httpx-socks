import httpcore
import httpx
# noinspection PyPackageRequirements
import pytest

from httpx_socks import (
    ProxyType,
    AsyncProxyTransport,
    ProxyError,
    ProxyConnectionError,
    ProxyTimeoutError,
)
from tests.conftest import (
    SOCKS5_IPV4_HOST, SOCKS5_IPV4_PORT,
    LOGIN, PASSWORD, SKIP_IPV6_TESTS, SOCKS5_IPV4_URL, SOCKS5_IPV6_URL,
    SOCKS4_URL, HTTP_PROXY_URL)

# HTTP_TEST_URL = 'http://httpbin.org/ip'
# HTTPS_TEST_URL = 'https://httpbin.org/ip'
HTTP_TEST_URL = 'http://check-host.net/ip'
HTTPS_TEST_URL = 'https://check-host.net/ip'

HTTP_URL_DELAY_3_SEC = 'http://httpbin.org/delay/3'


@pytest.mark.parametrize('url', (HTTP_TEST_URL, HTTPS_TEST_URL))
@pytest.mark.parametrize('rdns', (True, False))
@pytest.mark.trio
async def test_socks5_proxy_ipv4(url, rdns):
    transport = AsyncProxyTransport.from_url(SOCKS5_IPV4_URL, rdns=rdns)
    async with httpx.AsyncClient(transport=transport) as client:
        resp = await client.get(url)
        assert resp.status_code == 200


@pytest.mark.trio
async def test_socks5_proxy_with_invalid_credentials():
    transport = AsyncProxyTransport(
        proxy_type=ProxyType.SOCKS5,
        proxy_host=SOCKS5_IPV4_HOST,
        proxy_port=SOCKS5_IPV4_PORT,
        username=LOGIN,
        password=PASSWORD + 'aaa',
    )
    with pytest.raises(ProxyError):
        async with httpx.AsyncClient(transport=transport) as client:
            await client.get(HTTP_TEST_URL)


@pytest.mark.trio
async def test_socks5_proxy_with_read_timeout():
    transport = AsyncProxyTransport(
        proxy_type=ProxyType.SOCKS5,
        proxy_host=SOCKS5_IPV4_HOST,
        proxy_port=SOCKS5_IPV4_PORT,
        username=LOGIN,
        password=PASSWORD,
    )
    timeout = httpx.Timeout(2, connect_timeout=32)
    with pytest.raises(httpcore.ReadTimeout):
        async with httpx.AsyncClient(transport=transport,
                                     timeout=timeout) as client:
            await client.get(HTTP_URL_DELAY_3_SEC)


@pytest.mark.trio
async def test_socks5_proxy_with_connect_timeout():
    transport = AsyncProxyTransport(
        proxy_type=ProxyType.SOCKS5,
        proxy_host=SOCKS5_IPV4_HOST,
        proxy_port=SOCKS5_IPV4_PORT,
        username=LOGIN,
        password=PASSWORD,
    )
    timeout = httpx.Timeout(32, connect_timeout=0.001)
    with pytest.raises(ProxyTimeoutError):
        async with httpx.AsyncClient(transport=transport,
                                     timeout=timeout) as client:
            await client.get(HTTP_TEST_URL)


@pytest.mark.trio
async def test_socks5_proxy_with_invalid_proxy_port(unused_tcp_port):
    transport = AsyncProxyTransport(
        proxy_type=ProxyType.SOCKS5,
        proxy_host=SOCKS5_IPV4_HOST,
        proxy_port=unused_tcp_port,
        username=LOGIN,
        password=PASSWORD,
    )
    with pytest.raises(ProxyConnectionError):
        async with httpx.AsyncClient(transport=transport) as client:
            await client.get(HTTP_TEST_URL)


@pytest.mark.skipif(SKIP_IPV6_TESTS, reason='TravisCI doesn`t support ipv6')
@pytest.mark.trio
async def test_socks5_proxy_ipv6():
    transport = AsyncProxyTransport.from_url(SOCKS5_IPV6_URL)
    async with httpx.AsyncClient(transport=transport) as client:
        resp = await client.get(HTTP_TEST_URL)
        assert resp.status_code == 200


@pytest.mark.parametrize('url', (HTTP_TEST_URL, HTTPS_TEST_URL))
@pytest.mark.parametrize('rdns', (True, False))
@pytest.mark.trio
async def test_socks4_proxy(url, rdns):
    transport = AsyncProxyTransport.from_url(SOCKS4_URL, rdns=rdns, )
    async with httpx.AsyncClient(transport=transport) as client:
        resp = await client.get(url)
        assert resp.status_code == 200


@pytest.mark.parametrize('url', (HTTP_TEST_URL, HTTPS_TEST_URL))
@pytest.mark.trio
async def test_http_proxy(url):
    transport = AsyncProxyTransport.from_url(HTTP_PROXY_URL)
    async with httpx.AsyncClient(transport=transport) as client:
        resp = await client.get(url)
        assert resp.status_code == 200