import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Dashboard from "./pages/Dashboard";
import LiveGameView from "./components/game/LiveGameView";
import StatsDashboard from "./components/stats/StatsDashboard";
import SocialHub from "./components/social/SocialHub";
import AICoach from "./components/training/AICoach";
import NotFound from "./pages/NotFound";
import React from 'react';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import { ScoringVariantSelector } from './components/scoring/ScoringVariants';
import { GameConfigDialog } from './components/game/GameConfig';
import { theme } from './theme';
import { Community } from './pages/Community';
import { Profile } from './pages/Profile';
import { Progress } from './pages/Progress';

const queryClient = new QueryClient();

export const App: React.FC = () => {
  const [selectedVariant, setSelectedVariant] = React.useState<ScoringVariant | null>(null);
  const [configOpen, setConfigOpen] = React.useState(false);

  const handleVariantSelect = (variant: ScoringVariant) => {
    setSelectedVariant(variant);
    setConfigOpen(true);
  };

  const handleGameStart = (config: GameConfig) => {
    // Initialize game with selected variant and config
    console.log('Starting game with:', { variant: selectedVariant, config });
  };

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/community" element={<Community />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/progress" element={<Progress />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
