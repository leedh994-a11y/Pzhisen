import ChatBox from "@/components/ChatBox";
import SerpSearchBox from "@/components/SerpSearchBox";
import TweetComposer from "@/components/TweetComposer";

export default function Page() {
  return (
    <main style={{ padding: "32px 16px 64px" }}>
      <header style={{ maxWidth: 720, margin: "0 auto 32px" }}>
        <p style={{ margin: 0, fontSize: 14, letterSpacing: "0.08em", textTransform: "uppercase" }}>
          Pzhisen
        </p>
        <h1 style={{ margin: "8px 0 0", fontSize: 36, lineHeight: 1.1 }}>
          Agent console
        </h1>
        <p style={{ margin: "12px 0 0", color: "#444", maxWidth: 520 }}>
          Frontend only calls <code>/api/chat</code>, <code>/api/serp</code>, or{" "}
          <code>/api/tweet</code>. Provider keys stay in Vercel env.
        </p>
      </header>
      <ChatBox />
      <div style={{ height: 48 }} />
      <SerpSearchBox />
      <div style={{ height: 48 }} />
      <TweetComposer />
    </main>
  );
}
