// main.tsx
import ReactDOM from "react-dom/client";
import "./index.css";
import {RouterProvider} from "react-router-dom";
import {CreateRouter} from "./CreateRouter.tsx";
import {AuthProvider} from "./AuthProvider.tsx";
import DarkModeToggle from './layout/DarkModeToggle.tsx';
import Copyright from './layout/Copyright.tsx';


ReactDOM.createRoot(document.getElementById("root")!).render(<AuthProvider>
    <div className="min-h-screen flex flex-col transition-colors duration-300 bg-gray-100 dark:bg-gray-900">
        <DarkModeToggle/>
        <RouterProvider router={CreateRouter()}/>
        <Copyright/>
    </div>
</AuthProvider>);
