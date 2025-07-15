# Servicio Webhook API - Rappi Contact Center

API para procesar webhooks con FastAPI e integrar con Amazon Connect para el centro de contacto de Rappi.

## Estructura del proyecto
```
.
├── app/
│   ├── __init__.py
│   ├── main.py             # Código principal de la API
│   ├── dynamo.py           # Funciones para interactuar con DynamoDB
│   └── contact_reason_mapping.py # Mapeo de categorías de contacto
├── create-conversation/
│   ├── dispatcher.py       # Código heredado (referencia)
│   ├── kinesis_streaming.py # Código heredado (referencia)
│   └── requirements.txt    # Dependencias del proyecto heredado
├── Dockerfile              # Configuración para crear la imagen Docker
├── requirements.txt        # Dependencias de Python
└── docker-compose.yml      # Configuración para desarrollo local
```

## Criterios de Aceptación
- **AC-1**: Creación exitosa - Dado un payload válido de manual-review, cuando se invoca el endpoint, la API responde 201 con body.conversation.id = <caseId> y se crea un contacto + caso en Amazon Connect.
- **AC-2**: Customer Profile - Dado que el customer.id no existe en Amazon Customer Profiles, cuando se procesa la solicitud, se crea el perfil con los atributos enviados y se agrega la clave RappiId.
- **AC-3**: Campos obligatorios - Dado que faltan customer.id, conversation.subject, conversation.channel o conversation.sentAt, la API devuelve 400 Bad Request con mensaje de error específico.
- **AC-4**: Mapping de custom fields - Dado que conversation.customFields contiene claves válidas (order_id, country, etc.), cuando se crea el caso, cada campo se guarda en Amazon Cases según el mapeo DynamoDB (get_fileds_id).

## Variables de Entorno Requeridas
```
API_KEY - Clave de API para autenticación
WEBHOOK_ID - ID del webhook (default: createConversation)
DOMAIN_ID - ID del dominio de Amazon Connect Cases
DOMAIN_CUSTOMER_PROFILE_ID - ID del dominio de Amazon Customer Profiles
TEMPLATE_CASE_ID - ID de la plantilla para la creación de casos
CONNECT_PROFILE_ARN - ARN para perfiles de Connect
DYNAMODB_TABLE_NAME - Nombre de la tabla DynamoDB para mapeo de campos
AWS_REGION_NAME - Región de AWS
SECRET_NAME - ARN del secreto para credenciales de Rappi
RAPPI_MICROSERVICES_BASE_URL - URL base para microservicios de Rappi
```

## Desarrollo local

1. Configura las variables de entorno en el archivo `docker-compose.yml`.

2. Construir y ejecutar con Docker Compose:
   ```
   docker-compose up --build
   ```

3. O construir manualmente la imagen y ejecutarla:
   ```
   # Construir la imagen
   docker build -t create-conversation .
   
   # Ejecutar el contenedor (incluir todas las variables de entorno requeridas)
   docker run -p 8000:8000 -e API_KEY=your_api_key_here -e WEBHOOK_ID=createConversation -e DOMAIN_ID=your_domain_id -e DOMAIN_CUSTOMER_PROFILE_ID=your_profile_domain -e TEMPLATE_CASE_ID=your_template_id -e CONNECT_PROFILE_ARN=your_profile_arn -e DYNAMODB_TABLE_NAME=your_dynamo_table -e AWS_REGION_NAME=your_aws_region -e SECRET_NAME=your_secret_name -e RAPPI_MICROSERVICES_BASE_URL=your_rappi_url create-conversation
   ```

4. La API estará disponible en: `http://localhost:8000`

## Endpoints

### POST /v1/hooks/web/{webhook_id}

Crea un nuevo contacto y caso en Amazon Connect.

- **Headers requeridos**:
  - `Content-Type: application/json`
  - `Authorization: Bearer {API_KEY}`

- **Ejemplo de cuerpo de la petición**:
  ```json
  {
    "customer": {
      "id": "12345",
      "name": "John Doe",
      "phone": "1234567890",
      "email": "john@example.com",
      "externalId": "ext-12345",
      "userBlocked": false,
      "loyalty": "gold",
      "country": "CO",
      "rfmSegment": "high-value"
    },
    "conversation": {
      "subject": "Issue with my order",
      "sentAt": "2023-07-11T15:30:00Z",
      "channel": "web",
      "articleId": "art-12345",
      "externalId": "ext-conv-12345",
      "customFields": {
        "order_id": "ord-12345",
        "country": "CO",
        "chat_id": "chat-12345",
        "type_category_hc": "sn_org_mp.sn_org_pa.sn_org_pi"
      }
    }
  }
  ```

- **Ejemplo de respuesta exitosa (201 Created)**:
  ```json
  {
    "conversation": {
      "id": "case-12345"
    }
  }
  ```

### GET /health

Endpoint para verificar el estado del servicio.

- **Respuesta**:
  ```json
  {
    "status": "healthy"
  }
  ```

## Despliegue en ECS

Para desplegar en AWS ECS:

1. Construir la imagen Docker:
   ```
   docker build -t nombre-de-tu-imagen .
   ```

2. Etiquetar la imagen para tu repositorio ECR:
   ```
   docker tag nombre-de-tu-imagen:latest tu-repo-ecr.amazonaws.com/nombre-de-tu-imagen:latest
   ```

3. Enviar la imagen a ECR:
   ```
   docker push tu-repo-ecr.amazonaws.com/nombre-de-tu-imagen:latest
   ```

4. Configura la definición de tarea en ECS con todas las variables de entorno necesarias mencionadas anteriormente.