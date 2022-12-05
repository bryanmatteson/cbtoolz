import hmac
import os
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Tuple
from urllib.parse import parse_qsl, urlencode

import httpx


class AwsSigV4Auth(httpx.Auth):
    region: str
    session_token: Optional[str]
    secret_key: str
    access_key: str
    service: str

    def __init__(
        self,
        service: str,
        *,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        session_token: Optional[str] = None,
        region: Optional[str] = None,
    ) -> None:
        self.service = service
        if access_key is None and secret_key is None:
            access_key, secret_key = get_aws_credentials_from_env()
        if access_key is None or secret_key is None:
            access_key, secret_key = get_aws_credentials_from_file()

        self.access_key = access_key or ""
        self.secret_key = secret_key or ""
        self.session_token = session_token or os.getenv("AWS_SESSION_TOKEN", None)
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    def auth_flow(self, req: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        if not self.access_key or not self.secret_key:
            yield req
            return

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        req.headers["X-Amz-Date"] = timestamp

        if self.session_token:
            req.headers["X-Amz-Security-Token"] = self.session_token

        params: Dict[str, Any] = dict(parse_qsl(req.url.query.decode("utf-8"), keep_blank_values=True))
        query = urlencode(sorted(params.items()))

        # https://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
        canonical_headers = "".join("{0}:{1}\n".format(k.lower(), req.headers[k]) for k in sorted(req.headers))
        signed_headers = ";".join(k.lower() for k in sorted(req.headers))
        payload_hash = sha256(req.content).hexdigest()
        canonical_request = "\n".join(
            [req.method, req.url.path or "/", query, canonical_headers, signed_headers, payload_hash]
        )

        # https://docs.aws.amazon.com/general/latest/gr/sigv4-create-string-to-sign.html
        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = "/".join([timestamp[0:8], self.region, self.service, "aws4_request"])
        canonical_request_hash = sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = "\n".join([algorithm, timestamp, credential_scope, canonical_request_hash])

        # https://docs.aws.amazon.com/general/latest/gr/sigv4-calculate-signature.html
        key = "AWS4{0}".format(self.secret_key).encode("utf-8")
        key = hmac.new(key, timestamp[0:8].encode("utf-8"), sha256).digest()
        key = hmac.new(key, self.region.encode("utf-8"), sha256).digest()
        key = hmac.new(key, self.service.encode("utf-8"), sha256).digest()
        key = hmac.new(key, "aws4_request".encode("utf-8"), sha256).digest()
        signature = hmac.new(key, string_to_sign.encode("utf-8"), sha256).hexdigest()

        # https://docs.aws.amazon.com/general/latest/gr/sigv4-add-signature-to-request.html
        authorization = "{0} Credential={1}/{2}, SignedHeaders={3}, Signature={4}".format(
            algorithm, self.access_key, credential_scope, signed_headers, signature,
        )

        req.headers["X-Amz-Content-Sha256"] = payload_hash
        req.headers["Authorization"] = authorization
        yield req


def get_aws_credentials_from_env() -> Tuple[Optional[str], Optional[str]]:
    access_key = os.getenv("AWS_ACCESS_KEY_ID", None)
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", None)
    return (access_key, secret_key)


def get_aws_credentials_from_file() -> Tuple[Optional[str], Optional[str]]:
    credentials_path = Path(os.getenv("AWS_SHARED_CREDENTIALS_FILE", "~/.aws/credentials")).expanduser()
    if not credentials_path.exists() or not credentials_path.is_file():
        return (None, None)

    import configparser

    with credentials_path.open() as f_in:
        config = configparser.ConfigParser()
        config.read_file(f_in, source=credentials_path.as_posix())
        return (
            config.get("default", "aws_access_key_id", fallback=None),
            config.get("default", "aws_secret_access_key", fallback=None),
        )
