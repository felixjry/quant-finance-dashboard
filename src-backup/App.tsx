import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Navigation } from "./components/Navigation";
import { MarketTicker } from "./components/MarketTicker";
import Index from "./pages/Index";
import SingleAsset from "./pages/SingleAsset";
import Portfolio from "./pages/Portfolio";
import PaperTrading from "./pages/PaperTrading";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <div className="min-h-screen bg-background">
          <MarketTicker />
          <Navigation />
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/single-asset" element={<SingleAsset />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/paper-trading" element={<PaperTrading />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
