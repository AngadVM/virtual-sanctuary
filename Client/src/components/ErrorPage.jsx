export default function ErrorPage() {
    return (
      <>
        <main className="grid min-h-full place-items-center bg-black px-6 py-24 sm:py-32 lg:px-8">
          <div className="text-center">
            <p className="text-6xl font-semibold text-red-400">404</p>
            <h1 className="mt-4 text-5xl font-semibold tracking-tight text-balance text-gray-200 sm:text-7xl">
              Page not found
            </h1>
            <p className="mt-6 text-lg font-medium text-pretty text-gray-500 sm:text-xl/8">
              Sorry, we couldn’t find the page you’re looking for.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <a
                href="#"
                className="rounded-md bg-gray-200 px-3.5 py-2.5 text-sm font-semibold text-black shadow-xs hover:bg-gray-300 focus-visible:outline-2 focus-visible:outline-offset-2 "
              >
                Go back home
              </a>
              <a href="#" className="text-sm font-semibold text-gray-200 hover:underline">
                Contact support <span aria-hidden="true">&rarr;</span>
              </a>
            </div>
          </div>
        </main>
      </>
    )
  }
  