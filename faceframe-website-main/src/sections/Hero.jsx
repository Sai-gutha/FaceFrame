import Link from "next/link"
import Image from "next/image"
import ScrollButton from "../components/ScrollButton"

const Hero = () => {

  return (
    <section id="hero-section" className="relative md:h-auto lg:h-[calc(100vh-190px)] 2xl:h-[700px]">

      <div className="container grid grid-cols-1 lg:grid-cols-2 gap-6 py-12 lg:py-16">
        
        {/* Left Side Text */}
        <div className="z-10 md:text-center lg:text-left max-w-full  lg:max-w-full  lg:pt-0 2xl:pe-[4rem]">
          <h4 className="reveal hidden md:block text-base lg:text-lg 2xl:text-xl font-semibold text-gray-500 mb-5 md:mb-5">
            GLASSES SHOPPING MADE EASY
          </h4>

          <h1 className="reveal delay-200 capitalize text-[46px] font-semibold md:text-5xl lg:text-[52px] xl:text-header 2xl:text-7xl leading-tight md:font-medium mb-6 md:mb-8">
            Find your <br className="block lg:hidden"/> <span className=" text-[52px] md:text-header font-bold text-transparent bg-gradient-to-r from-[#3c85d3] via-[#8DBBEB] to-[#3c85d3] bg-clip-text [background-size:200%_200%] [animation:var(--animate-gradient-text)]">
  perfect glasses 
</span> <br className="hidden md:block lg:hidden"/>
 with the power of AI.
          </h1>

          <p className="reveal delay-400 text-lg xl:text-lg 2xl:text-xl text-gray-700 mb-6 md:mb-8">
            FaceFrame uses machine learning and facial recognition to recommend glasses tailored to your unique features. <span className="hidden lg:block">Built by a team of students across business and tech, we're redefining the way people shop for glasses.</span>
          </p>

          <div className="flex md:justify-center lg:justify-normal w-full gap-4 sm:gap-6">
            <a href="https://youtu.be/YhlZamspXWY?si=cCYS0nw2M1Ha4Uih" target="_blank" className="reveal reveal-left delay-1000 ">
              <button className="primary-btn w-full sm:w-auto">View Demo</button>
            </a>
            <ScrollButton
              targetId="how-it-works-section"
              className="secondary-btn w-full sm:w-auto"
              
            >
              Learn More
            </ScrollButton>


          </div>
        </div>

        {/* Right Side Image */}
        <div
          className="md:relative md:w-[31.25rem] md:h-[28.125rem] lg:absolute lg:w-[47%] lg:h-full lg:bottom-0 lg:right-0 lg:rounded-tl-[135px] overflow-hidden lg:border-t-2 lg:border-l-2 border-gray-300 hidden lg:block"
        >
          <Image
            src="/images/heroimg.jpeg"
            alt="Hero Image"
            fill
            priority
            style={{ objectFit: "cover" }}
          />
        </div>
      </div>
    </section>
  )
}

export default Hero
