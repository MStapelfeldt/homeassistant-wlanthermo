# Model version options for config flow
MODEL_OPTIONS = [
	"Link V1",
	"Mini-V2",
	"Mini-V3",
	"Nano V3"
]

DOMAIN = "wlanthermo"
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = 5
CONF_BASE_PATH = "base_path"
CONF_VERIFY_SSL = "verify_ssl"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

ATTR_HOST = "host"
ATTR_DEVICE_INFO = "device_info"
API_TIMEOUT = 8

PLATFORMS = ["sensor", "switch", "number", "select", "text", "button"]

SERVICE_SET_CHANNEL = "set_channel"
SERVICE_SET_PITMASTER = "set_pitmaster"
SERVICE_SET_SYSTEM = "set_system"
SERVICE_CONFIG_RESET = "config_reset"
