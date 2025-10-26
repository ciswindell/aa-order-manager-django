"use client"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from "@/components/ui/command"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { Check, ChevronsUpDown, X } from "lucide-react"
import * as React from "react"

export interface MultiSelectOption {
  label: string
  value: string | number
}

interface MultiSelectProps {
  options: MultiSelectOption[]
  selected: (string | number)[]
  onChange: (selected: (string | number)[]) => void
  placeholder?: string
  emptyText?: string
  className?: string
  onSearchChange?: (value: string) => void
  disabled?: boolean
  emptyAction?: React.ReactNode
}

export function MultiSelect({
  options,
  selected,
  onChange,
  placeholder = "Select items...",
  emptyText = "No items found.",
  className,
  onSearchChange,
  disabled,
  emptyAction,
}: MultiSelectProps) {
  const [open, setOpen] = React.useState(false)

  const handleSelect = (value: string | number) => {
    const newSelected = selected.includes(value)
      ? selected.filter((item) => item !== value)
      : [...selected, value]
    onChange(newSelected)
  }

  const handleRemove = (value: string | number, e: React.MouseEvent) => {
    e.stopPropagation()
    onChange(selected.filter((item) => item !== value))
  }

  const selectedOptions = options.filter((option) =>
    selected.includes(option.value)
  )

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled}
          className={cn(
            "w-full justify-between h-auto min-h-10 py-2",
            className
          )}
        >
          <div className="flex flex-wrap gap-1 flex-1">
            {selectedOptions.length > 0 ? (
              selectedOptions.map((option) => (
                <Badge
                  key={option.value}
                  variant="secondary"
                  className="mr-1 mb-1"
                >
                  {option.label}
                  <span
                    role="button"
                    tabIndex={0}
                    className="ml-1 ring-offset-background rounded-full outline-hidden focus:ring-2 focus:ring-ring focus:ring-offset-2 cursor-pointer"
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        handleRemove(option.value, e as any)
                      }
                    }}
                    onMouseDown={(e) => {
                      e.preventDefault()
                      e.stopPropagation()
                    }}
                    onClick={(e) => handleRemove(option.value, e)}
                  >
                    <X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
                  </span>
                </Badge>
              ))
            ) : (
              <span className="text-muted-foreground">{placeholder}</span>
            )}
          </div>
          <ChevronsUpDown className="h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent 
        className={cn(
          "w-full p-0",
          emptyAction && "max-h-[500px]"
        )} 
        align="start"
      >
        <Command>
          <CommandInput 
            placeholder="Search..." 
            onValueChange={onSearchChange}
          />
          <CommandList className={cn(emptyAction && "max-h-[450px] overflow-y-auto")}>
            <CommandEmpty>
              <div className="text-center py-2">
                <div className="text-sm text-muted-foreground">{emptyText}</div>
                {emptyAction && <div className="mt-2 px-2 pb-2">{emptyAction}</div>}
              </div>
            </CommandEmpty>
            <CommandGroup>
              {options.map((option) => {
                const isSelected = selected.includes(option.value)
                return (
                  <CommandItem
                    key={option.value}
                    onSelect={() => handleSelect(option.value)}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        isSelected ? "opacity-100" : "opacity-0"
                      )}
                    />
                    {option.label}
                  </CommandItem>
                )
              })}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}

