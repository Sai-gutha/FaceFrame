import Image from "next/image";

const HowItWorks = () => {
  return (
    <section id="how-it-works-section" className="bg-[#F2F2F2] border-t border-t-gray-300">
      <div className="container py-24 md:py-32 px-6 sm:px-10 lg:px-0">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 md:gap-16">
          {/* Column 1 */}
          <div className="text-center lg:text-left pe-0 lg:pe-10">
            <h4 className="reveal text-base font-semibold md:text-lg mb-4">HOW IT WORKS</h4>
            <h1 className="reveal text-[43px] md:text-secondary-header leading-[1.1] font-semibold mb-8 lg:max-w-xl">
              Finding frames just got easier.
            </h1>
            <hr className="reveal border-secondary-blue border-2 mx-auto lg:mx-0 w-[30%] mb-8" />
            <div className="reveal">
            <a href="https://youtu.be/YhlZamspXWY?si=cCYS0nw2M1Ha4Uih" target="_blank">
              <button className="primary-btn w-1/2 md:w-full h-[56px] hover:scale-[1.02] transition-transform mb-5 md:mb-10">
                View Demo
              </button>
            </a>

            </div>
            

            <h3 className="reveal hidden md:block text-xl sm:text-2xl font-semibold mb-6 lg:text-3xl text-gray-600">
              We’ve made finding your perfect pair simple. Here’s how it works:
            </h3>
          </div>

          {/* Column 2 */}
          <div className="hidden lg:block relative h-[180px] sm:h-[240px] md:h-[400px] lg:h-[500px]">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 md:left-auto md:right-[0rem] md:translate-x-0 md:-top-[12rem]">
              <div className="relative w-[20rem] h-[15rem] md:w-[35rem] md:h-[36rem] rounded-lg border border-gray-300 overflow-hidden">
                <Image
                  src="/images/image3.jpeg"
                  alt="lady with glasses"
                  fill
                  style={{ objectFit: "cover" }}
                  priority
                />
              </div>
            </div>
          </div>
        </div>

        {/* Steps */}
        <div className="flex flex-col px-4 sm:px-14 mt-20 gap-20">
          {/* Step 1 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div className="reveal delay-200">

              <h1 className="reveal text-[40px] lg:text-header leading-tight font-semibold mb-6">
                Visit a store
              </h1>
              <hr className="reveal border-gray-500 border-2 w-[30%] mb-6" />
              <p className="reveal text-lg lg:text-xl">
              Visit a FaceFrame partner location or kiosk to begin your personalized eyewear experience. Our in-store stations are equipped with everything needed for a quick and seamless face scan.
              </p>
            </div>
            <div className="reveal px-8 md:px-14 order-first mx-auto md:order-last">
              <Image
              src="/01.png"
              alt="test"
              height={500}
              width={500}
              
              />
            </div>
          </div>

          <hr className="border-gray-400 border-[0.5px] w-full mx-auto" />

          {/* Step 2 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div className="reveal mx-auto ">
              <Image
              src="/02.png"
              alt="test"
              height={500}
              width={500}
              
              />
            </div>
            <div className="reveal delay-200 text-right md:text-left">
              <h1 className="reveal text-[40px] lg:text-header leading-tight font-semibold mb-6">
                Scan your face
              </h1>
              <hr className="reveal border-gray-500 border-2 w-[30%] ms-auto md:ms-0 mb-6" />
              <p className="reveal text-lg lg:text-xl">
                Using advanced AI, FaceFrame scans your facial structure in seconds to
                understand your unique features. This helps us determine which frame shapes
                and sizes will complement your face best.
              </p>
            </div>
          </div>

          <hr className="border-gray-400 border-[0.5px] w-full mx-auto" />

          {/* Step 3 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div className="reveal delay-200">
              <h1 className="reveal text-[40px] lg:text-header leading-tight font-semibold mb-6">
                Find your fit
              </h1>
              <hr className="reveal border-gray-500 border-2 w-[30%] mb-6" />
              <p className="reveal text-lg lg:text-xl">
                Instantly receive frame recommendations tailored to your face shape, style
                preferences, and fit. Try them on virtually or in person, and walk out with
                glasses made just for you.
              </p>
            </div>
            <div className="reveal order-first mx-auto md:order-last">
              <Image
              src="/03.png"
              alt="test"
              height={500}
              width={500}
              
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
