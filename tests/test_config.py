import os
import unittest
from unittest import TestCase

from cfg_load import Configuration

from py4ai.config import get_all_configuration_file, merge_confs
from py4ai.config.configurations import (
    AuthConfig,
    AuthenticationServiceConfig,
    BaseConfig,
    FileSystemConfig,
    LoggingConfig,
)
from tests import DATA_FOLDER

os.environ["USER"] = os.environ.get("USER", "py4ai")
TEST_DATA_PATH = DATA_FOLDER


class TempConfig(BaseConfig):
    @property
    def logging(self):
        return LoggingConfig(self.sublevel("logging"))

    @property
    def fs(self):
        return FileSystemConfig(self.sublevel("fs"))

    @property
    def auth(self):
        return AuthConfig(self.sublevel("auth"))

    @property
    def authentication(self):
        return AuthenticationServiceConfig(self.sublevel("authentication"))


test_file = "defaults.yml"
os.environ["CONFIG_FILE"] = os.path.join(TEST_DATA_PATH, test_file)

root = os.path.join("this", "is", "a", "folder")
credentials = os.path.join(root, "myfolder", "credentials.p")

config = TempConfig(
    BaseConfig(
        merge_confs(
            get_all_configuration_file(), os.path.join(TEST_DATA_PATH, "defaults.yml")
        )
    ).sublevel("test")
)


class TestBaseConfig(TestCase):
    def test_sublevel(self):
        self.assertEqual(
            config.sublevel("fs").to_dict(),
            {
                "root": root,
                "folders": {"python": "myfolder"},
                "files": {"credentials": credentials},
            },
        )

    def test_getValue(self):
        self.assertEqual(config.getValue("fs")["root"], root)
        self.assertRaises(KeyError, config.getValue, "folders")

    def test_safeGetValue(self):
        self.assertEqual(config.safeGetValue("fs")["root"], root)
        self.assertIsNone(config.safeGetValue("folders"))

    def test_update_dict(self):

        new_config = config.update({"test": {"fs": {"root": "new_folder"}}})

        self.assertEqual(new_config.getValue("test")["fs"]["root"], "new_folder")
        self.assertEqual(
            new_config.config.meta["updated_params"],
            {"test": {"fs": {"root": "new_folder"}}},
        )

    def test_update_conf(self):
        new_config = config.update(
            Configuration(
                cfg_dict={"test": {"fs": {"root": "new_folder"}}},
                meta={"parse_datetime": None, "filepath": TEST_DATA_PATH},
            )
        )

        self.assertEqual(new_config.getValue("test")["fs"]["root"], "new_folder")
        self.assertEqual(
            new_config.config.meta["updated_params"],
            {"test": {"fs": {"root": "new_folder"}}},
        )
        self.assertEqual(
            new_config.config.meta["filepath"],
            TEST_DATA_PATH,
        )
        self.assertIsNone(new_config.config.meta["parse_datetime"])


class TestFileSystemConfig(TestCase):
    def test_root(self):
        self.assertEqual(config.fs.root, root)

    def test_getFolder(self):
        self.assertEqual(config.fs.getFolder("python"), "myfolder")

    def test_getFile(self):
        self.assertEqual(config.fs.getFile("credentials"), credentials)


class TestAuthConfig(TestCase):
    def test_method(self):
        self.assertEqual(config.auth.method, "file")

    def test_filename(self):
        self.assertEqual(config.auth.filename, credentials)

    def test_user(self):
        self.assertEqual(config.auth.user, "userID")

    def test_password(self):
        self.assertEqual(config.auth.password, "passwordID")


class TestAuthenticationServiceConfig(TestCase):
    def test_secured(self):
        self.assertTrue(config.authentication.secured, "passwordID")

    def test_ap_name(self):
        self.assertEqual(config.authentication.ap_name, "cb")

    def test_cors(self):
        self.assertEqual(config.authentication.cors, "http://0.0.0.0:10001")

    def test_jwt_free_endpoints(self):
        self.assertEqual(
            config.authentication.jwt_free_endpoints,
            [
                "/api/v1/health/",
                "/api/v1/auth/login",
                "/api/v1/apidocs",
                "/api/v1/swagger.json",
                "/api/v1/salesforce/",
                "/api/v1/openBanking/",
            ],
        )

    def test_auth_service(self):
        self.assertEqual(config.authentication.auth_service.url, "http://0.0.0.0:10005")
        self.assertEqual(
            config.authentication.auth_service.check, "/tokens/{tok}/check"
        )
        self.assertEqual(
            config.authentication.auth_service.decode, "/tokens/{tok}/decode"
        )

    def test_check_service(self):
        self.assertEqual(
            config.authentication.check_service.url, "http://0.0.0.0:10001"
        )
        self.assertEqual(
            config.authentication.check_service.login, "/authentication/login"
        )
        self.assertEqual(
            config.authentication.check_service.logout, "/authentication/logout"
        )


class TestLoggingConfig(TestCase):
    def test_level(self):
        self.assertEqual(config.logging.level, "DEBUG")

    def test_filename(self):
        self.assertEqual(config.logging.filename, os.path.join("logs", "tests.log"))

    def test_default_config_file(self):
        self.assertEqual(
            config.logging.default_config_file,
            os.path.join("confs", "logConfDefaults.yaml"),
        )

    def test_capture_warnings(self):
        self.assertTrue(config.logging.capture_warnings)


if __name__ == "__main__":
    unittest.main()
