from typing import List

import pytest

from starlite import OpenAPIConfig
from starlite.app import DEFAULT_OPENAPI_CONFIG
from starlite.enums import MediaType
from starlite.openapi.controller import OpenAPIController
from starlite.status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND
from starlite.testing import create_test_client
from tests.openapi.utils import PersonController, PetController

root_paths: List[str] = ["", "/part1", "/part1/part2"]


def test_default_redoc_cdn_urls() -> None:
    with create_test_client([PersonController, PetController], openapi_config=DEFAULT_OPENAPI_CONFIG) as client:
        response = client.get("/schema/redoc")
        default_redoc_version = "next"
        default_redoc_js_bundle = (
            f"https://cdn.jsdelivr.net/npm/redoc@{default_redoc_version}/bundles/redoc.standalone.js"
        )
        assert client.app.openapi_config is not None
        assert client.app.openapi_config.openapi_controller.redoc_js_url == default_redoc_js_bundle
        assert default_redoc_js_bundle in response.text


def test_default_swagger_ui_cdn_urls() -> None:
    with create_test_client([PersonController, PetController], openapi_config=DEFAULT_OPENAPI_CONFIG) as client:
        response = client.get("/schema/swagger")
        default_swagger_bundles = [
            f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{OpenAPIController.swagger_ui_version}/swagger-ui.css",
            f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{OpenAPIController.swagger_ui_version}/swagger-ui-bundle.js",
            f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{OpenAPIController.swagger_ui_version}/swagger-ui-standalone-preset.js",
        ]
        assert client.app.openapi_config is not None
        assert client.app.openapi_config.openapi_controller.swagger_css_url in default_swagger_bundles
        assert client.app.openapi_config.openapi_controller.swagger_ui_bundle_js_url in default_swagger_bundles
        assert (
            client.app.openapi_config.openapi_controller.swagger_ui_standalone_preset_js_url in default_swagger_bundles
        )
        assert all(cdn_url in response.text for cdn_url in default_swagger_bundles)


def test_default_stoplight_elements_cdn_urls() -> None:
    with create_test_client([PersonController, PetController], openapi_config=DEFAULT_OPENAPI_CONFIG) as client:
        response = client.get("/schema/elements")
        default_stoplight_elements_bundles = [
            f"https://unpkg.com/@stoplight/elements@{OpenAPIController.stoplight_elements_version}/styles.min.css",
            f"https://unpkg.com/@stoplight/elements@{OpenAPIController.stoplight_elements_version}/web-components.min.js",
        ]
        assert client.app.openapi_config is not None
        assert (
            client.app.openapi_config.openapi_controller.stoplight_elements_css_url
            in default_stoplight_elements_bundles
        )
        assert (
            client.app.openapi_config.openapi_controller.stoplight_elements_js_url in default_stoplight_elements_bundles
        )
        assert all(cdn_url in response.text for cdn_url in default_stoplight_elements_bundles)


def test_redoc_with_google_fonts() -> None:
    with create_test_client([PersonController, PetController], openapi_config=DEFAULT_OPENAPI_CONFIG) as client:
        response = client.get("/schema/redoc")
        google_font_cdn = "https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700"
        assert client.app.openapi_config is not None
        assert client.app.openapi_config.openapi_controller.redoc_google_fonts is True
        assert google_font_cdn in response.text


def test_redoc_without_google_fonts() -> None:
    class OfflineOpenAPIController(OpenAPIController):
        """test class for usage in a couple "offline" tests and for without Google fonts test."""

        redoc_google_fonts = False

    offline_config = OpenAPIConfig(title="Starlite API", version="1.0.0", openapi_controller=OfflineOpenAPIController)
    with create_test_client([PersonController, PetController], openapi_config=offline_config) as client:
        response = client.get("/schema/redoc")
        assert "fonts.googleapis.com" not in response.text


def test_openapi_redoc_offline() -> None:
    class OfflineOpenAPIController(OpenAPIController):
        """test class for usage in a couple "offline" tests and for without Google fonts test."""

        redoc_js_url = "https://offline_location/redoc.standalone.js"

    offline_config = OpenAPIConfig(title="Starlite API", version="1.0.0", openapi_controller=OfflineOpenAPIController)
    with create_test_client([PersonController, PetController], openapi_config=offline_config) as client:
        response = client.get("/schema/redoc")
        assert OfflineOpenAPIController.redoc_js_url in response.text


def test_openapi_swagger_offline() -> None:
    class OfflineOpenAPIController(OpenAPIController):
        """test class for usage in a couple "offline" tests and for without Google fonts test."""

        swagger_css_url = "https://offline_location/swagger-ui-css"
        swagger_ui_bundle_js_url = "https://offline_location/swagger-ui-bundle.js"
        swagger_ui_standalone_preset_js_url = "https://offline_location/swagger-ui-standalone-preset.js"

    offline_config = OpenAPIConfig(title="Starlite API", version="1.0.0", openapi_controller=OfflineOpenAPIController)
    with create_test_client([PersonController, PetController], openapi_config=offline_config) as client:
        response = client.get("/schema/swagger")
        assert OfflineOpenAPIController.swagger_css_url in response.text
        assert OfflineOpenAPIController.swagger_ui_bundle_js_url in response.text
        assert OfflineOpenAPIController.swagger_ui_standalone_preset_js_url in response.text


def test_openapi_stoplight_elements_offline() -> None:
    class OfflineOpenAPIController(OpenAPIController):
        """test class for usage in a couple "offline" tests and for without Google fonts test."""

        stoplight_elements_css_url = "https://offline_location/spotlight-styles.mins.css"
        stoplight_elements_js_url = "https://offline_location/spotlight-web-components.min.js"

    offline_config = OpenAPIConfig(title="Starlite API", version="1.0.0", openapi_controller=OfflineOpenAPIController)
    with create_test_client([PersonController, PetController], openapi_config=offline_config) as client:
        response = client.get("/schema/elements")
        assert OfflineOpenAPIController.stoplight_elements_css_url in response.text
        assert OfflineOpenAPIController.stoplight_elements_js_url in response.text


@pytest.mark.parametrize("root_path", root_paths)
def test_openapi_root(root_path: str) -> None:
    with create_test_client(
        [PersonController, PetController], openapi_config=DEFAULT_OPENAPI_CONFIG, root_path=root_path
    ) as client:
        response = client.get("/schema")
        assert response.status_code == HTTP_200_OK
        assert response.headers["content-type"].startswith(MediaType.HTML.value)


@pytest.mark.parametrize("root_path", root_paths)
def test_openapi_redoc(root_path: str) -> None:
    with create_test_client(
        [PersonController, PetController], openapi_config=DEFAULT_OPENAPI_CONFIG, root_path=root_path
    ) as client:
        response = client.get("/schema/redoc")
        assert response.status_code == HTTP_200_OK
        assert response.headers["content-type"].startswith(MediaType.HTML.value)


@pytest.mark.parametrize("root_path", root_paths)
def test_openapi_swagger(root_path: str) -> None:
    with create_test_client(
        [PersonController, PetController], openapi_config=DEFAULT_OPENAPI_CONFIG, root_path=root_path
    ) as client:
        response = client.get("/schema/swagger")
        assert response.status_code == HTTP_200_OK
        assert response.headers["content-type"].startswith(MediaType.HTML.value)


@pytest.mark.parametrize("root_path", root_paths)
def test_openapi_stoplight_elements(root_path: str) -> None:
    with create_test_client(
        [PersonController, PetController], openapi_config=DEFAULT_OPENAPI_CONFIG, root_path=root_path
    ) as client:
        response = client.get("/schema/elements/")
        assert response.status_code == HTTP_200_OK
        assert response.headers["content-type"].startswith(MediaType.HTML.value)


def test_openapi_root_not_allowed() -> None:
    with create_test_client(
        [PersonController, PetController],
        openapi_config=OpenAPIConfig(
            title="Starlite API",
            version="1.0.0",
            enabled_endpoints={"swagger", "elements", "openapi.json", "openapi.yaml"},
        ),
    ) as client:
        response = client.get("/schema")
        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.headers["content-type"].startswith(MediaType.HTML.value)


def test_openapi_redoc_not_allowed() -> None:
    with create_test_client(
        [PersonController, PetController],
        openapi_config=OpenAPIConfig(
            title="Starlite API",
            version="1.0.0",
            enabled_endpoints={"swagger", "elements", "openapi.json", "openapi.yaml"},
        ),
    ) as client:
        response = client.get("/schema/redoc")
        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.headers["content-type"].startswith(MediaType.HTML.value)


def test_openapi_swagger_not_allowed() -> None:
    with create_test_client(
        [PersonController, PetController],
        openapi_config=OpenAPIConfig(
            title="Starlite API",
            version="1.0.0",
            enabled_endpoints={"redoc", "elements", "openapi.json", "openapi.yaml"},
        ),
    ) as client:
        response = client.get("/schema/swagger")
        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.headers["content-type"].startswith(MediaType.HTML.value)


def test_openapi_stoplight_elements_not_allowed() -> None:
    with create_test_client(
        [PersonController, PetController],
        openapi_config=OpenAPIConfig(
            title="Starlite API",
            version="1.0.0",
            enabled_endpoints={"redoc", "swagger", "openapi.json", "openapi.yaml"},
        ),
    ) as client:
        response = client.get("/schema/elements/")
        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.headers["content-type"].startswith(MediaType.HTML.value)
