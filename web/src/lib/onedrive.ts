import { fetcher } from "./fetcher";

interface OneDriveOAuthSetupResponse {
  auth_url: string;
}

interface OneDriveOAuthSetupParams {
  isAdmin: boolean;
  name: string;
}

export const setupOneDriveOAuth = async ({
  isAdmin,
  name,
}: OneDriveOAuthSetupParams): Promise<[string | null, string | null]> => {
  try {
    const response = await fetcher("/api/manage/admin/connector/onedrive/oauth/authorize", {
      method: "POST",
      body: JSON.stringify({
        is_admin: isAdmin,
        name,
      }),
    });

    const data = (await response.json()) as OneDriveOAuthSetupResponse;
    return [data.auth_url, null];
  } catch (error) {
    return [null, "Failed to setup OneDrive OAuth"];
  }
}; 