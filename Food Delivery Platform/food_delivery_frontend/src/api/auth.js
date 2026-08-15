import client from "./client";

export const login = (username, password) =>
  client.post("/accounts/login/", { username, password }).then((r) => r.data);

export const register = (payload) =>
  client.post("/accounts/register/", payload).then((r) => r.data);

export const logout = (refresh) =>
  client.post("/accounts/logout/", { refresh }).then((r) => r.data);

export const getProfile = () => client.get("/accounts/profile/").then((r) => r.data);

export const updateProfile = (payload) =>
  client.patch("/accounts/profile/", payload).then((r) => r.data);

export const changePassword = (payload) =>
  client.post("/accounts/change-password/", payload).then((r) => r.data);

export const requestPasswordReset = (email) =>
  client.post("/accounts/password-reset/", { email }).then((r) => r.data);

export const confirmPasswordReset = (payload) =>
  client.post("/accounts/password-reset/confirm/", payload).then((r) => r.data);

export const listAddresses = () => client.get("/accounts/addresses/").then((r) => r.data);

export const createAddress = (payload) =>
  client.post("/accounts/addresses/", payload).then((r) => r.data);

export const deleteAddress = (id) => client.delete(`/accounts/addresses/${id}/`);
