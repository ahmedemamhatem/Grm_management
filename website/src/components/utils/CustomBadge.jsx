import { Plus } from 'lucide-react'
import React from 'react'
import { Badge } from '../ui/badge'

const CustomBadge = ({ title }) => {
    return (
        <div className='flex items-center gap-2'>
            <Badge>
                <Plus />
            </Badge>
            <p className='font-bold'>{title}</p>
        </div>
    )
}

export default CustomBadge