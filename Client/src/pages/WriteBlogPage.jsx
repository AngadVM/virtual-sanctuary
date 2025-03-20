import React from "react";
import { IconButton, Typography } from "@material-tailwind/react";
import { ArrowRightIcon, ArrowLeftIcon } from "@heroicons/react/24/outline";
 
export default function WriteBlogPage() {
  const [active, setActive] = React.useState(1);
 
  const next = () => {
    if (active === 10) return;
 
    setActive(active + 1);
  };
 
  const prev = () => {
    if (active === 1) return;
 
    setActive(active - 1);
  };
 
  return (
    <div className="pagination">
      <div className="flex items-center gap-8">
      <IconButton
        size="sm"
        color="white"
        variant="outlined"
        onClick={prev}
        disabled={active === 1}
      >
        <ArrowLeftIcon strokeWidth={2} className="h-4 w-4" color="white" />
      </IconButton>
      <Typography className="font-normal text-gray-400">
        Page <strong className="text-gray-300">{active}</strong> of{" "}
        <strong className="text-gray-300">10</strong>
      </Typography>
      <IconButton
        size="sm"
        color="white"
        variant="outlined"
        onClick={next}
        disabled={active === 10}
      >
        <ArrowRightIcon strokeWidth={2} className="h-4 w-4" color="white" />
      </IconButton>
    </div>
    </div>
    
  );
}