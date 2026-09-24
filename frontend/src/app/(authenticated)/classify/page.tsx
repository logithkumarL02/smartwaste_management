import { createClient } from "@/lib/supabase/server";
import ClassifyClient from "@/components/classification/ClassifyClient";

export default async function ClassifyPage() {
  const supabase = await createClient();
  const { data: { session } } = await supabase.auth.getSession();
  return <ClassifyClient token={session?.access_token ?? ""} />;
}
