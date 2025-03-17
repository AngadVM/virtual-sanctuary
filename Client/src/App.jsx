// REACT LIB IMPORTS
import React from "react";

import { BrowserRouter, Routes, Route } from "react-router-dom";

// PAGE ROUTES IMPORTS
import MainPage from "@pages/MainPage.jsx";
import LoginPage from "@pages/LoginPage.jsx";
import RegisterPage from "@pages/RegisterPage.jsx";
import ExplorePage from "@pages/ExplorePage.jsx";
import GalleryPage from "@pages/GalleryPage.jsx";
import LearnMorePage from "@pages/LearnMorePage.jsx";
import ErrorPage from "@pages/ErrorPage.jsx";
import WriteBlogPage from "./pages/WriteBlogPage";


//? CODE
const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/write" element={<WriteBlogPage />} />
        <Route path="/explore" element={<ExplorePage />} />
        <Route path="/gallery" element={<GalleryPage />} />
        <Route path="/learn-more" element={<LearnMorePage />} />
        <Route path="*" element={<ErrorPage />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
