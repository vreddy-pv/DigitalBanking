package com.digitalbanking.ops.consumer;

import com.digitalbanking.ops.service.OpsCaseService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.stereotype.Component;

import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class ComplaintEventConsumer {

    private final OpsCaseService opsCaseService;

    @RabbitListener(queues = "#{@opsCasesQueue.name}")
    public void handle(Map<String, Object> event,
                       @Header(value = "amqp_receivedRoutingKey", defaultValue = "") String routingKey) {
        String ticketId = (String) event.getOrDefault("ticketId", "unknown");
        log.info("ComplaintEventConsumer received routingKey={} ticketId={}", routingKey, ticketId);
        try {
            if ("complaint.created".equals(routingKey)) {
                opsCaseService.createCase(event);
            } else if ("complaint.investigated".equals(routingKey)) {
                opsCaseService.updateWithInvestigation(event);
            } else {
                log.debug("Ignoring unhandled routing key: {}", routingKey);
            }
        } catch (Exception ex) {
            log.error("Error handling event routingKey={} ticketId={}: {}", routingKey, ticketId, ex.getMessage(), ex);
        }
    }
}
