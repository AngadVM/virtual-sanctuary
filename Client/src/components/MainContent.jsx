import react from "react";
import iucnImage from "@assets/iucn.png"
import visImage from "@assets/visualisation.png"

import blogsFrame from "@assets/blogsFrame.svg"
import galleryImage from "@assets/galleryImage.svg"


const scrollToAbout = (e) => {
  e.preventDefault();
  const aboutSection = document.querySelector('.about');
  if (aboutSection) {
    aboutSection.scrollIntoView({ behavior: 'smooth' });
  }
};

export default function MainContent() {
  return (
    
      <div>
        <div className="bg-black">
          <div className="mx-auto max-w-2xl px-6 lg:max-w-7xl lg:px-8 items-center justify-center">
            <p className="py-1 text-gray-500 italic">what do we got here?</p>
            <div className="text-4xl text-gray-300 font-extrabold">About</div>
            <div className="mt-10 grid gap-4 sm:mt-16 lg:grid-cols-3 lg:grid-rows-2">
              <div className="relative lg:row-span-2">
                <div className="absolute inset-px rounded-lg bg-white lg:rounded-l-[2rem]"></div>
                <div className="relative flex h-full flex-col overflow-hidden rounded-[calc(var(--radius-lg)+1px)] lg:rounded-l-[calc(2rem+1px)]">
                  <div className="px-8 pt-8 pb-3 sm:px-10 sm:pt-10 sm:pb-0">
                    <p className="mt-2 text-lg tracking-tight text-black font-semibold max-lg:text-center">
                      Write your experiences
                    </p>
                    <p className="mt-2 max-w-lg text-sm/6 text-gray-700 max-lg:text-center">
                      Sign up, create a blog and post your wildlife content on our platform!
                    </p>
                  </div>
                  <div className="@container relative min-h-[30rem] w-full grow max-lg:mx-auto max-lg:max-w-sm">
                    <div className="absolute  overflow-hidden p-2">
                      <img
                        className="size-full object-left-top"
                        src={blogsFrame}
                        alt=""
                      />
                    </div>
                  </div>
                </div>
                <div className="pointer-events-none absolute inset-px rounded-lg ring-1 shadow-sm ring-black/5 lg:rounded-l-[2rem]"></div>
              </div>
              <div className="relative max-lg:row-start-1">
                <div className="absolute inset-px rounded-lg bg-white  max-lg:rounded-t-[2rem]"></div>
                <div className="relative flex h-full flex-col overflow-hidden rounded-[calc(var(--radius-lg)+1px)] max-lg:rounded-t-[calc(2rem+1px)]">
                  <div className="px-8  sm:px-10 sm:pt-10">
                    <p className="mt-2 text-lg font-semibold tracking-tight text-black max-lg:text-center">
                      Visualizing wildlife
                    </p>
                    <p className="mt-2 max-w-lg text-sm/6 text-gray-700 max-lg:text-center">
                    Explore wildlife with derived visualization.
                    </p>
                  </div>
                  <div className="flex flex-1 items-center justify-center px-8 max-lg:pt-10 max-lg:pb-12 sm:px-10 lg:pb-2">
                    <img
                      className="w-full p-2 max-lg:max-w-xs rounded-3xl"
                      src={visImage}
                      alt=""
                    />
                  </div>
                </div>
                <div className="pointer-events-none absolute inset-px rounded-lg ring-1 shadow-sm ring-black/5 max-lg:rounded-t-[2rem]"></div>
              </div>
              <div className="relative max-lg:row-start-3 lg:col-start-2 lg:row-start-2">
                <div className="absolute inset-px rounded-lg bg-white"></div>
                <div className="relative flex h-full flex-col overflow-hidden rounded-[calc(var(--radius-lg)+1px)]">
                  <div className="px-8 pt-8 sm:px-10 sm:pt-10">
                    <p className="mt-2 text-lg font-semibold tracking-tight text-black max-lg:text-center">
                      WildGallery
                    </p>
                    <p className="mt-2 max-w-lg text-sm/6 text-gray-700 max-lg:text-center">
                      Browse through different angled clicks of wildlife creatures.
                    </p>
                  </div>
                  <div className="@container flex flex-1 items-center rounded-3xl max-lg:py-6 lg:pb-2">
                    <img
                      className="w-full p-4 max-lg:max-w-xs rounded-3xl"
                      src={galleryImage}
                      alt=""
                    />
                  </div>
                </div>
                <div className="pointer-events-none absolute inset-px rounded-lg ring-1 shadow-sm ring-black/5"></div>
              </div>
              <div className="relative lg:row-span-2">
                <div className="absolute inset-px rounded-lg bg-white max-lg:rounded-b-[2rem] lg:rounded-r-[2rem]"></div>
                <div className="relative flex h-full flex-col overflow-hidden rounded-[calc(var(--radius-lg)+1px)] max-lg:rounded-b-[calc(2rem+1px)] lg:rounded-r-[calc(2rem+1px)]">
                  <div className="px-8 pt-8 pb-3 sm:px-10 sm:pt-10 sm:pb-0">
                    <p className="mt-2 text-lg font-semibold tracking-tight text-black max-lg:text-center">
                      Scientic exploration
                    </p>
                    <p className="mt-2 max-w-lg text-sm/6 text-gray-700 max-lg:text-center">
                      Get scientic information and witness real-time conservation status updates and connect with nature's finest creatures.
                    </p>
                  </div>
                  <div className="relative min-h-[30rem] w-full grow">
                    <div className="absolute top-10 right-0 bottom-0 left-10">
                      <div className="flex">
                      <img src={iucnImage} alt="" className=" h-full rounded-3xl"/>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  );
}
