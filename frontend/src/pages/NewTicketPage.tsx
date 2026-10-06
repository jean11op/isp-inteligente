import PageHeader from "@/components/ui/PageHeader";
import ChatbotReport from "@/features/tickets/components/ChatbotReport";

export default function NewTicketPage() {
  return (
    <>
      <PageHeader title="Reportar una incidencia" />
      <ChatbotReport />
    </>
  );
}