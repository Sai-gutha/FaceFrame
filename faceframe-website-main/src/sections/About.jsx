import Image from "next/image"

const About = () => {
  return (
    <section id='about-section' className='relative about-gradient clip-about-shape overflow-hidden'>
        
        <div className="hidden lg:block w-[45%] pt-5 pb-5 ms-auto text-center">
            <h1 className="text-white text-xl font-bold items-center"><span className=" text-xl text-gray-600">90% </span> found their perfect fit in minutes</h1>
        </div>

       <div className="container">
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-4 pt-16 lg:pt-32 pb-26'>

            {/* Column 1 */}
            <div className="relative md:w-[420px] md:h-[420px] lg:w-[520px] lg:h-[520px] lg:justify-normal hidden md:flex md:items-center md:justify-center md:mx-auto md:mb-8 lg:mb-0 lg:mx-0 ">
                <Image
                    src="/images/about_img2.jpg"
                    alt="lady with glasses"
                    fill
                    className="object-cover"
                />
            </div>


            {/* Column 2 */}
            <div className="text-center md:text-left">
                <h4 className="reveal font-semibold text-white text-base lg:text-lg mb-4" >ABOUT US</h4>
                <h1 className="reveal text-[43px] lg:text-secondary-header leading-[1.1] text-white font-semibold mb-8">No measuring, no second-guessing.</h1>

                <hr className="reveal border-white border-2 mx-auto md:mx-0 w-[30%] mb-8" />
                {/* Divider
                <div className="flex md:hidden w-1/2 mx-auto my-8 items-center"> 
                    <hr className="border-[1px] border-white w-full mx-auto "/>

                    <Image
                    src="/logo.svg"
                    alt="white logo"
                    height={50}
                    width={50}
                    className="px-3"/>

                    <hr className="border-[1px] border-white w-full mx-auto "/>
                </div> */}

                <p className="reveal text-lg text-white mb-6">At FaceFrame we believe choosing the right frames should be simple, accurate, and even fun. With our AI-powered virtual try-on tool, there’s no need for measurements or uncertainty, just a seamless way to find what fits you best.</p>

                 <div className="flex items-center justify-center py-8  md:hidden">
                 <Image
                        src="/images/aboutimg-sm.png"
                        alt="lady with glasses"
                        width={500}
                        height={500}
                        className="object-cover"
                    />

                 </div>
                

               
                <div className="flex flex-col md:flex-row gap-6 mt-12">
                    <div className="reveal sm:reveal-left reveal-right mb-5 md:mb-0 text-left md:text-left">
                        <h3 className="text-4xl text-white font-semibold mb-5">Vision</h3>
                        <hr className="border-[1px] border-white my-4 w-full md:hidden"/>
                        <p className="text-lg text-white">FaceFrame envisions a future where finding the perfect pair of glasses is effortless and personalized. </p>

                    </div>

                    <div className="reveal reveal-right delay-200 text-right md:text-left">
                        <h3 className="text-4xl text-white font-semibold mb-5">Mission</h3>
                        <hr className="border-[1px] border-white my-4 w-full ms-auto md:hidden"/>
                        <p className="text-lg text-white">Our mission is to empower individuals to find eyewear that fits their face and style with confidence. </p>

                    </div>
                </div>
            </div>

            
        </div>

        </div>

    </section>
  )
}

export default About