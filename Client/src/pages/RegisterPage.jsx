import { useState } from "react";
import "./RegisterPage.css";
import { Typography, Input, Button } from "@material-tailwind/react";
import { EyeSlashIcon, EyeIcon } from "@heroicons/react/24/solid";

export function RegisterPage() {
  const [passwordShown, setPasswordShown] = useState(false);
  const togglePasswordVisiblity = () => setPasswordShown((cur) => !cur);

  return (
    <section className="grid text-center h-screen items-center p-8">
      <div>
        <Typography variant="h3" color="blue-gray" className="mb-2">
          Sign Up to Virtuary
        </Typography>
        <Typography className="mb-16 text-gray-600 font-normal text-[18px]">
          Join our bloglike platform to explore and learn about wildlife
        </Typography>
        <form action="#" className="mx-auto max-w-[24rem] text-left">
          <div className="mb-6 usernamebox">
            <label htmlFor="email">
              <Typography
                variant="small"
                className="mb-2 block font-medium text-gray-300"
              >
                Your Username
              </Typography>
            </label>
            <Input
              id="email"
              color="gray"
              size="lg"
              type="email"
              name="email"
              placeholder="abc123"
              className="w-full placeholder:opacity-100 custom-border"
              labelProps={{
                className: "hidden",
              }}
            />
          </div>

          <div className="mb-6 emailbox">
            <label htmlFor="email">
              <Typography
                variant="small"
                className="mb-2 block font-medium text-gray-300"
              >
                Your Email
              </Typography>
            </label>
            <Input
              id="email"
              color="gray"
              size="lg"
              type="email"
              name="email"
              placeholder=" name@mail.com"
              className="w-full placeholder:opacity-100 custom-border"
              labelProps={{
                className: "hidden",
              }}
            />
          </div>
          <div className="mb-6 passwordbox">
            <label htmlFor="password">
              <Typography
                variant="small"
                className="mb-2 block font-medium text-gray-300"
              >
                Password
              </Typography>
            </label>
            <Input
              size="lg"
              placeholder="********"
              labelProps={{
                className: "hidden",
              }}
              className="w-full placeholder:opacity-100 custom-border"
              type={passwordShown ? "text" : "password"}
              icon={
                <i onClick={togglePasswordVisiblity}>
                  {passwordShown ? (
                    <EyeIcon className="h-5 w-5" />
                  ) : (
                    <EyeSlashIcon className="h-5 w-5" />
                  )}
                </i>
              }
            />
          </div>
          <Button
            color="white"
            size="lg"
            className="mt-6 text-black bg-gray-200"
            fullWidth
          >
            sign up
          </Button>
          <Button
            variant="outlined"
            size="lg"
            className="mt-3 flex h-12 items-center justify-center gap-2 text-gray-300"
            fullWidth
          >
            <img
              src={`https://www.material-tailwind.com/logos/logo-google.png`}
              alt="google"
              className="h-6 w-6"
            />{" "}
            sign up with google
          </Button>
          
        </form>
      </div>
    </section>
  );
}

export default RegisterPage;
