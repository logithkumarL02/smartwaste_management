import { createClient } from "@/lib/supabase/server";
import DashboardClient from "@/components/dashboard/DashboardClient";

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  const { data: predictions } = await supabase.from("predictions").select("*")
    .eq("user_id", user!.id).order("created_at", { ascending: false }).limit(100);
  const { data: profile } = await supabase.from("profiles").select("display_name").eq("user_id", user!.id).single();
  return (
    <DashboardClient
      predictions={predictions ?? []}
      displayName={profile?.display_name || user?.email?.split("@")[0] || "User"}
    />
  );
}
