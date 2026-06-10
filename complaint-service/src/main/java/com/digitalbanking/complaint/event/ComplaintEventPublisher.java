package com.digitalbanking.complaint.event;

import com.digitalbanking.complaint.config.RabbitMQConfig;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class ComplaintEventPublisher {

    private final RabbitTemplate rabbitTemplate;

    public void publish(ComplaintCreatedEvent event) {
        try {
            rabbitTemplate.convertAndSend(
                    RabbitMQConfig.EXCHANGE_NAME,
                    RabbitMQConfig.ROUTING_KEY,
                    event
            );
            log.info("Published ComplaintCreatedEvent: ticketId={} type={}",
                    event.getTicketId(), event.getComplaintType());
        } catch (Exception ex) {
            // Log and continue — complaint is already persisted; ops can replay from DB
            log.error("Failed to publish ComplaintCreatedEvent for ticketId={}: {}",
                    event.getTicketId(), ex.getMessage());
        }
    }
}
