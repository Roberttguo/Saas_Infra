RETRY = 30
RETRY_CLEANUP = 3
#for HCM and HCX cloud
BASE_HCX_API = "/hybridity/api"
HCX_SESSION = BASE_HCX_API+"/sessions"
HCX_SAAS_ADAPTER_SITE = BASE_HCX_API+"/saas/site"

#for HCXSaas portal
BASE_HCX_SAAS_API = "/api/v1"
HCXSAAS_SRV_ONBOARD_REQ = BASE_HCX_SAAS_API+"/site-onboarding/request-registration"

#For csp authotication
CSP_TOKEN_URI="/csp/gateway/am/api/auth/api-tokens/authorize?refresh_token=%s"
CSP_URL="console-stg.cloud.vmware.com"