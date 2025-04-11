import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/clerk-react";

export default function ClerkAuth() {
  return (
    <>
      <SignedOut>
        <SignInButton className="font-medium hover:bg-black hover:text-white transition duration-500 border-1 border-gray-400 rounded-full px-3 hover:cursor-pointer py-2" ><span>Sign In &rarr;</span></SignInButton>
      </SignedOut>
      <SignedIn>
        <UserButton />
      </SignedIn>
    </>
  );
}