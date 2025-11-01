"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"

interface Account {
  id: string
  name: string
}

// T027: Create account selection page component
export default function SelectBasecampAccount() {
  const router = useRouter()
  // T028: State management
  const [accounts, setAccounts] = useState<Account[]>([])
  const [selectedAccountId, setSelectedAccountId] = useState<string>("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  // T029: Fetch pending accounts on page load
  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const response = await fetch(
          "http://localhost:8000/api/integrations/basecamp/pending-accounts/",
          {
            credentials: "include",
            headers: {
              "Content-Type": "application/json",
            },
          }
        )

        const data = await response.json()

        if (response.ok && data.accounts) {
          setAccounts(data.accounts)
          setLoading(false)
        } else {
          // T030: Handle session expiry
          setError(data.message || "Session expired. Please connect again.")
          setLoading(false)
        }
      } catch (err) {
        // T030: Handle network errors
        setError("Failed to load accounts. Please try again.")
        setLoading(false)
      }
    }

    fetchAccounts()
  }, [])

  // T032: Connect button handler
  const handleConnect = async () => {
    if (!selectedAccountId) return

    setSubmitting(true)
    setError(null)

    try {
      const response = await fetch(
        "http://localhost:8000/api/integrations/basecamp/select-account/",
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ account_id: selectedAccountId }),
        }
      )

      const data = await response.json()

      if (response.ok) {
        // T033: Success redirect
        router.push("/dashboard?basecamp=connected")
      } else {
        // T034: Error handling
        setError(data.message || "Failed to connect account")
        setSubmitting(false)
      }
    } catch (err) {
      // T034: Network error handling
      setError("Network error. Please try again.")
      setSubmitting(false)
    }
  }

  // T035: Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-lg">Loading accounts...</p>
        </div>
      </div>
    )
  }

  // T034: Error state with recovery
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="max-w-md w-full p-6 space-y-4 text-center">
          <p className="text-red-600 text-lg">{error}</p>
          <Button onClick={() => router.push("/integrations")} className="w-full">
            Connect Again
          </Button>
        </div>
      </div>
    )
  }

  // T031: RadioGroup UI
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-md space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Select Basecamp Account
          </h1>
          <p className="text-gray-600 mt-2">
            You have access to multiple Basecamp accounts. Which one would you
            like to connect?
          </p>
        </div>

        <RadioGroup
          value={selectedAccountId}
          onValueChange={setSelectedAccountId}
          className="space-y-3"
        >
          {accounts.map((account) => (
            <div
              key={account.id}
              className="flex items-center space-x-3 p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
            >
              <RadioGroupItem value={account.id} id={account.id} />
              <Label htmlFor={account.id} className="cursor-pointer flex-1 text-base">
                {account.name}
              </Label>
            </div>
          ))}
        </RadioGroup>

        {/* T035: Connect button with loading state */}
        <Button
          onClick={handleConnect}
          disabled={!selectedAccountId || submitting}
          className="w-full"
          size="lg"
        >
          {submitting ? "Connecting..." : "Connect Selected Account"}
        </Button>

        <p className="text-sm text-gray-500 text-center">
          You can disconnect and change accounts later in your settings
        </p>
      </div>
    </div>
  )
}

