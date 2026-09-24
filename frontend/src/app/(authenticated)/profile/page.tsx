import { createClient } from "@/lib/supabase/server";
import ProfileClient from "@/components/profile/ProfileClient";

export default async function ProfilePage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  const { data: profile } = await supabase.from("profiles").select("*").eq("user_id", user!.id).single();
  const { count } = await supabase.from("predictions").select("*", { count:"exact", head:true }).eq("user_id", user!.id);
  return <ProfileClient user={user!} profile={profile} totalPredictions={count ?? 0} />;
}
