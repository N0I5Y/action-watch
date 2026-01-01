import { apiGet } from "./http";

export interface User {
    id: number;
    login: string;
    avatar_url: string;
    name?: string;
}

export interface Installation {
    id: number;
    account_login: string;
    account_avatar_url: string;
    subscription?: {
        isPro: boolean;
        status: string;
        currentPeriodEnd: string | null;
    };
}

export interface CurrentUserResponse {
    user: User;
    installations: Installation[];
}

export async function getCurrentUser(): Promise<CurrentUserResponse> {
    return apiGet<CurrentUserResponse>("/api/auth/me");
}
