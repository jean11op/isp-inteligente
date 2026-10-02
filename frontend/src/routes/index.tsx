import { createBrowserRouter } from "react-router";
import HomePage from "../pages/HomePage";
import { PATHS } from "./paths";

export const router = createBrowserRouter([
  { path: PATHS.home, element: <HomePage /> },
]);