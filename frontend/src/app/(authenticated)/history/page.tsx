import { createClient } from "@/lib/supabase/server";
import HistoryClient from "@/components/history/HistoryClient";

export default async function HistoryPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  const { data: predictions } = await supabase.from("predictions").select("*")
    .eq("user_id", user!.id).order("created_at", { ascending: false }).limit(200);
  return <HistoryClient predictions={predictions ?? []} />;
}
