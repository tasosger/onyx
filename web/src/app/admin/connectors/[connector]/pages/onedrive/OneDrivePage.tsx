import { useCallback, useState } from "react";
import { Title } from "@tremor/react";
import { usePopup } from "@/components/admin/connectors/Popup";
import { useConnectorForm } from "@/components/admin/connectors/Form";
import { useUser } from "@/lib/hooks";
import { setupOneDriveOAuth } from "@/lib/onedrive";
import { Button } from "@/components/Button";
import { TextFormField } from "@/components/admin/connectors/Field";
import { Formik, Form } from "formik";
import Cookies from "js-cookie";
import { Alert } from "@/components/Alert";

const ONEDRIVE_AUTH_IS_ADMIN_COOKIE_NAME = "onedrive_auth_is_admin";

const OneDriveJsonUploadSection = ({
  setPopup,
  appCredentialData,
  isAdmin,
  onSuccess,
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  if (appCredentialData?.client_id) {
    return (
      <div>
        <div>
          <p className="text-sm mb-1">Current Credentials:</p>
          <div className="text-sm font-mono bg-stone-100 p-2 rounded mb-2">
            <div>Client ID: {appCredentialData.client_id}</div>
          </div>
        </div>
        {!isAdmin && (
          <Alert type="info" className="mt-4">
            To change these credentials, please contact an administrator.
          </Alert>
        )}
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <Alert type="info" className="mt-2">
        Curators are unable to set up the OneDrive credentials. To add a
        OneDrive connector, please contact an administrator.
      </Alert>
    );
  }

  return (
    <div className="mt-2">
      <p className="text-sm mb-4">
        Follow the guide{" "}
        <a
          className="text-link"
          target="_blank"
          href="https://docs.onyx.app/connectors/onedrive"
          rel="noreferrer"
        >
          here
        </a>{" "}
        to set up Microsoft OAuth App in your organization.
      </p>
      <p className="text-sm mb-4">
        After setting up the OAuth app, download the credentials JSON and upload it here.
      </p>
      {error && <Alert type="error" className="mb-4">{error}</Alert>}
      <Button
        loading={isUploading}
        onClick={async () => {
          try {
            setIsUploading(true);
            setError("");
            // Upload logic here
            await onSuccess();
          } catch (err) {
            setError(err.message || "Failed to upload credentials");
          } finally {
            setIsUploading(false);
          }
        }}
      >
        Upload Credentials
      </Button>
    </div>
  );
};

const OneDriveAuthSection = ({
  setPopup,
  refreshCredentials,
  oneDrivePublicUploadedCredential,
  appCredentialData,
  connectorAssociated,
  user,
}) => {
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const isAdmin = user?.role === "admin";

  if (!isAdmin) {
    return (
      <Alert type="info" className="mb-4">
        Please contact an administrator to set up OneDrive authentication.
      </Alert>
    );
  }

  if (appCredentialData?.client_id) {
    return (
      <div className="text-sm mb-4">
        <p className="mb-4">
          Next, you must provide credentials via OAuth. This gives us read
          access to the docs you have access to in your OneDrive account.
        </p>
        <Button
          loading={isAuthenticating}
          onClick={async () => {
            try {
              setIsAuthenticating(true);
              const [authUrl, errorMsg] = await setupOneDriveOAuth({
                isAdmin: true,
                name: "OAuth (uploaded)",
              });
              if (authUrl) {
                Cookies.set(ONEDRIVE_AUTH_IS_ADMIN_COOKIE_NAME, "true", {
                  path: "/",
                });
                window.location.href = authUrl;
                return;
              }

              setPopup({
                message: errorMsg || "Failed to start OAuth flow",
                type: "error",
              });
            } catch (err) {
              setPopup({
                message: err.message || "Failed to authenticate",
                type: "error",
              });
            } finally {
              setIsAuthenticating(false);
            }
          }}
        >
          Authenticate with OneDrive
        </Button>
      </div>
    );
  }

  return (
    <Alert type="info">
      Please upload your OAuth Client Credential JSON in Step 1 before moving onto Step 2.
    </Alert>
  );
};

const OneDriveMain = () => {
  const { user } = useUser();
  const isAdmin = user?.role === "admin";
  const { setPopup } = usePopup();
  const { appCredentialData, oneDrivePublicUploadedCredential, connectorAssociated, handleRefresh } = useConnectorForm();

  return (
    <div className="space-y-6">
      <div>
        <Title className="mb-4">Step 1: Provide your Credentials</Title>
        <OneDriveJsonUploadSection
          setPopup={setPopup}
          appCredentialData={appCredentialData}
          isAdmin={isAdmin}
          onSuccess={handleRefresh}
        />
      </div>

      {isAdmin && appCredentialData?.client_id && (
        <div>
          <Title className="mb-4">Step 2: Authenticate with Onyx</Title>
          <OneDriveAuthSection
            setPopup={setPopup}
            refreshCredentials={handleRefresh}
            oneDrivePublicUploadedCredential={oneDrivePublicUploadedCredential}
            appCredentialData={appCredentialData}
            connectorAssociated={connectorAssociated}
            user={user}
          />
        </div>
      )}
    </div>
  );
};

export default OneDriveMain; 