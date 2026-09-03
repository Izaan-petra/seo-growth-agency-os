"""Production connector catalog and deterministic default registration."""

from __future__ import annotations

from seo_os.secrets import SecretResolver

from .ahrefs import AhrefsConnector
from .crux import ChromeUxReportConnector
from .ga4 import GoogleAnalytics4Connector
from .gsc import GoogleSearchConsoleConnector
from .pagespeed import PageSpeedInsightsConnector
from .registry import ConnectorRegistry
from .tabular import TabularConnector
from .transport import HttpTransport


def build_default_registry(
    *,
    transport: HttpTransport | None = None,
    secret_resolver: SecretResolver | None = None,
) -> ConnectorRegistry:
    shared = {"transport": transport, "secret_resolver": secret_resolver}
    return ConnectorRegistry(
        [
            GoogleSearchConsoleConnector(**shared),
            GoogleAnalytics4Connector(**shared),
            AhrefsConnector(**shared),
            PageSpeedInsightsConnector(**shared),
            ChromeUxReportConnector(**shared),
            TabularConnector(**shared),
        ]
    )
