
const Card = ({icon: Icon, name, desc}) => {
  return (
    <div className='card bg-white border border-gray-300 rounded-[20px] w-full md:max-w-[18rem] md:h-auto md:hover:scale-105 transition duration-300'>
      <div className='p-10'>
        <Icon className="text-secondary-blue size-12 md:size-14 mx-auto mb-4 md:mb-6"/>

        <h3 className="font-semibold text-xl mb-2">{name}</h3>
        <p className="text-base md:text-lg leading-[1.45]">{desc}</p>

      </div>

    </div>
  )
}

export default Card