// shared/lib/db/DataIntegrityValidator.js

const { 
  CATEGORY_TYPES, 
  RELATIONSHIP_TYPES, 
  RELATIONSHIP_DIRECTIONS,
  CATEGORY_CHARACTERISTICS,
  RELATIONSHIP_CHARACTERISTICS,
  THESIS_TYPES,
  THESIS_STYLES
} = require('../../constants/philosophy-constants');

class DataIntegrityValidator {
  constructor(databaseManager) {
    this.dbManager = databaseManager;
    this.validationResults = [];
  }

  async validateAllConcepts() {
    console.log('Starting data integrity validation...');
    this.validationResults = [];
    
    // Получение всех концепций из PostgreSQL
    const pgResult = await this.dbManager.postgresPool.query(
      'SELECT concept_id FROM concepts'
    );
    
    const conceptIds = pgResult.rows.map(row => row.concept_id);
    console.log(`Found ${conceptIds.length} concepts to validate`);
    
    for (const conceptId of conceptIds) {
      await this.validateConcept(conceptId);
    }
    
    return this.generateReport();
  }

  async validateConcept(conceptId) {
    const issues = [];
    
    try {
      // 1. Проверка наличия в PostgreSQL
      const pgResult = await this.dbManager.postgresPool.query(
        'SELECT * FROM concepts WHERE concept_id = $1',
        [conceptId]
      );
      
      if (pgResult.rows.length === 0) {
        issues.push({
          type: 'missing_in_postgres',
          severity: 'critical',
          description: `Concept ${conceptId} not found in PostgreSQL`
        });
        
        this.validationResults.push({
          conceptId,
          status: 'failed',
          issues
        });
        return;
      }
      
      const conceptMetadata = pgResult.rows[0];
      
      // 2. Проверка наличия в Neo4j
      const neo4jSession = this.dbManager.neo4jDriver.session();
      const neo4jResult = await neo4jSession.run(
        'MATCH (c:Concept {concept_id: $conceptId}) RETURN c',
        { conceptId }
      );
      
      if (neo4jResult.records.length === 0) {
        issues.push({
          type: 'missing_in_neo4j',
          severity: 'critical',
          description: `Concept ${conceptId} not found in Neo4j`
        });
      } else {
        // Проверка соответствия данных
        const neo4jConcept = neo4jResult.records[0].get('c').properties;
        if (neo4jConcept.name !== conceptMetadata.name) {
          issues.push({
            type: 'data_mismatch',
            severity: 'high',
            description: `Name mismatch: PostgreSQL="${conceptMetadata.name}", Neo4j="${neo4jConcept.name}"`,
            field: 'name'
          });
        }
      }
      
      // 3. Проверка категорий в Neo4j
      const categoriesResult = await neo4jSession.run(`
        MATCH (c:Concept {concept_id: $conceptId})-[:INCLUDES]->(cat:Category)
        RETURN count(cat) as categoryCount, collect(cat) as categories
      `, { conceptId });
      
      const categoryCount = categoriesResult.records[0].get('categoryCount').toNumber();
      const categories = categoriesResult.records[0].get('categories');
      
      if (categoryCount === 0) {
        issues.push({
          type: 'no_categories',
          severity: 'warning',
          description: `Concept ${conceptId} has no categories in Neo4j`
        });
      } else {
        // Проверка правильности типов категорий
        for (const category of categories) {
          const properties = category.properties;
          
          // Проверка наличия типа категории
          if (!properties.type) {
            issues.push({
              type: 'missing_category_type',
              severity: 'warning',
              description: `Category ${properties.category_id} (${properties.name}) has no type`,
              categoryId: properties.category_id
            });
          } else if (!Object.values(CATEGORY_TYPES).includes(properties.type)) {
            issues.push({
              type: 'invalid_category_type',
              severity: 'warning',
              description: `Category ${properties.category_id} (${properties.name}) has invalid type: ${properties.type}`,
              categoryId: properties.category_id,
              currentValue: properties.type
            });
          }
          
          // Проверка характеристик категории
          for (const characteristic of Object.values(CATEGORY_CHARACTERISTICS)) {
            if (properties[characteristic] === undefined || properties[characteristic] === null) {
              issues.push({
                type: 'missing_category_characteristic',
                severity: 'info',
                description: `Category ${properties.category_id} (${properties.name}) missing characteristic: ${characteristic}`,
                categoryId: properties.category_id,
                characteristic
              });
            }
          }
        }
      }
      
      // 4. Проверка отношений в Neo4j
      const relationshipsResult = await neo4jSession.run(`
        MATCH (c:Concept {concept_id: $conceptId})-[:INCLUDES]->(cat:Category)
        MATCH (cat)-[r:RELATED_TO]-(related:Category)
        WHERE related.concept_id = $conceptId
        RETURN count(r) as relationshipCount, collect(r) as relationships
      `, { conceptId });
      
      if (relationshipsResult.records.length > 0) {
        const relationshipCount = relationshipsResult.records[0].get('relationshipCount').toNumber();
        const relationships = relationshipsResult.records[0].get('relationships');
        
        if (relationshipCount === 0 && categoryCount > 1) {
          issues.push({
            type: 'disconnected_categories',
            severity: 'warning',
            description: `Concept ${conceptId} has multiple categories but no relationships between them`
          });
        } else if (relationshipCount > 0) {
          // Проверка правильности типов отношений
          for (const relationship of relationships) {
            const properties = relationship.properties;
            
            // Проверка типа отношения
            if (!properties.type) {
              issues.push({
                type: 'missing_relationship_type',
                severity: 'warning',
                description: `Relationship ${properties.relationship_id} has no type`,
                relationshipId: properties.relationship_id
              });
            } else if (!Object.values(RELATIONSHIP_TYPES).includes(properties.type)) {
              issues.push({
                type: 'invalid_relationship_type',
                severity: 'warning',
                description: `Relationship ${properties.relationship_id} has invalid type: ${properties.type}`,
                relationshipId: properties.relationship_id,
                currentValue: properties.type
              });
            }
            
            // Проверка направления отношения
            if (!properties.direction) {
              issues.push({
                type: 'missing_relationship_direction',
                severity: 'warning',
                description: `Relationship ${properties.relationship_id} has no direction`,
                relationshipId: properties.relationship_id
              });
            } else if (!Object.values(RELATIONSHIP_DIRECTIONS).includes(properties.direction)) {
              issues.push({
                type: 'invalid_relationship_direction',
                severity: 'warning',
                description: `Relationship ${properties.relationship_id} has invalid direction: ${properties.direction}`,
                relationshipId: properties.relationship_id,
                currentValue: properties.direction
              });
            }
            
            // Проверка характеристик отношения
            for (const characteristic of Object.values(RELATIONSHIP_CHARACTERISTICS)) {
              if (properties[characteristic] === undefined || properties[characteristic] === null) {
                issues.push({
                  type: 'missing_relationship_characteristic',
                  severity: 'info',
                  description: `Relationship ${properties.relationship_id} missing characteristic: ${characteristic}`,
                  relationshipId: properties.relationship_id,
                  characteristic
                });
              }
            }
          }
        }
      }
      
      await neo4jSession.close();
      
      // 5. Проверка тезисов в MongoDB
      const theses = await this.dbManager.mongodb
        .collection('theses')
        .find({ concept_id: conceptId })
        .toArray();
      
      if (theses.length === 0) {
        issues.push({
          type: 'no_theses',
          severity: 'info',
          description: `Concept ${conceptId} has no theses in MongoDB`
        });
      } else {
        // Проверка типов и стилей тезисов
        for (const thesis of theses) {
          // Проверка типа тезиса
          if (!thesis.type) {
            issues.push({
              type: 'missing_thesis_type',
              severity: 'warning',
              description: `Thesis ${thesis._id} has no type`,
              thesisId: thesis._id
            });
          } else if (!Object.values(THESIS_TYPES).includes(thesis.type)) {
            issues.push({
              type: 'invalid_thesis_type',
              severity: 'warning',
              description: `Thesis ${thesis._id} has invalid type: ${thesis.type}`,
              thesisId: thesis._id,
              currentValue: thesis.type
            });
          }
          
          // Проверка стиля тезиса
          if (thesis.style && !Object.values(THESIS_STYLES).includes(thesis.style)) {
            issues.push({
              type: 'invalid_thesis_style',
              severity: 'warning',
              description: `Thesis ${thesis._id} has invalid style: ${thesis.style}`,
              thesisId: thesis._id,
              currentValue: thesis.style
            });
          }
          
          // Проверка ссылок на категории
          if (thesis.related_categories && thesis.related_categories.length > 0) {
            // Проверим наличие каждой связанной категории в Neo4j
            await this.validateCategoryReferences(conceptId, thesis);
          }
        }
      }
      
      // 6. Проверка практического применения в MongoDB
      const practicalApplication = await this.dbManager.mongodb
        .collection('practicalApplications')
        .findOne({ concept_id: conceptId });
      
      if (!practicalApplication) {
        issues.push({
          type: 'no_practical_application',
          severity: 'info',
          description: `Concept ${conceptId} has no practical application data in MongoDB`
        });
      }
      
      // 7. Проверка данных синтеза, если концепция является результатом синтеза
      if (conceptMetadata.is_synthesis) {
        const synthesis = await this.dbManager.mongodb
          .collection('syntheses')
          .findOne({ concept_id: conceptId });
        
        if (!synthesis) {
          issues.push({
            type: 'missing_synthesis_data',
            severity: 'warning',
            description: `Concept ${conceptId} is marked as synthesis but has no synthesis data in MongoDB`
          });
        }
      }
      
      this.validationResults.push({
        conceptId,
        status: issues.length === 0 ? 'valid' : 'issues_found',
        issues
      });
      
    } catch (error) {
      this.validationResults.push({
        conceptId,
        status: 'error',
        error: error.message,
        issues
      });
    }
    
    return {
      conceptId,
      status: issues.length === 0 ? 'valid' : 'issues_found',
      issues
    };
  }

  async validateCategoryReferences(conceptId, thesis) {
    const issues = [];
    
    for (const categoryId of thesis.related_categories) {
      const neo4jSession = this.dbManager.neo4jDriver.session();
      const result = await neo4jSession.run(
        'MATCH (cat:Category {category_id: $categoryId, concept_id: $conceptId}) RETURN cat',
        { categoryId, conceptId }
      );
      await neo4jSession.close();
      
      if (result.records.length === 0) {
        issues.push({
          type: 'invalid_category_reference',
          severity: 'high',
          description: `Thesis ${thesis._id} references non-existent category ${categoryId}`,
          thesisId: thesis._id,
          categoryId
        });
      }
    }
    
    return issues;
  }

  async fixIntegrityIssues(conceptId, issues) {
    const fixes = [];
    
    for (const issue of issues) {
      try {
        switch (issue.type) {
          case 'missing_in_neo4j':
            await this.recreateConceptInNeo4j(conceptId);
            fixes.push({
              issue: issue.type,
              status: 'fixed',
              action: 'recreated_in_neo4j'
            });
            break;
          
          case 'data_mismatch':
            await this.syncDataFromPostgres(conceptId, issue.field);
            fixes.push({
              issue: issue.type,
              field: issue.field,
              status: 'fixed',
              action: 'synced_from_postgres'
            });
            break;
          
          case 'invalid_category_type':
            await this.fixCategoryType(issue.categoryId);
            fixes.push({
              issue: issue.type,
              categoryId: issue.categoryId,
              status: 'fixed',
              action: 'updated_category_type'
            });
            break;
          
          case 'invalid_relationship_type':
            await this.fixRelationshipType(issue.relationshipId);
            fixes.push({
              issue: issue.type,
              relationshipId: issue.relationshipId,
              status: 'fixed',
              action: 'updated_relationship_type'
            });
            break;
          
          case 'invalid_relationship_direction':
            await this.fixRelationshipDirection(issue.relationshipId);
            fixes.push({
              issue: issue.type,
              relationshipId: issue.relationshipId,
              status: 'fixed',
              action: 'updated_relationship_direction'
            });
            break;
          
          case 'invalid_thesis_type':
            await this.fixThesisType(issue.thesisId);
            fixes.push({
              issue: issue.type,
              thesisId: issue.thesisId,
              status: 'fixed',
              action: 'updated_thesis_type'
            });
            break;
          
          case 'invalid_thesis_style':
            await this.fixThesisStyle(issue.thesisId);
            fixes.push({
              issue: issue.type,
              thesisId: issue.thesisId,
              status: 'fixed',
              action: 'updated_thesis_style'
            });
            break;
          
          case 'no_categories':
            // Может потребоваться воссоздание из резервной копии
            fixes.push({
              issue: issue.type,
              status: 'manual_intervention_required',
              action: 'check_backups_or_recreate'
            });
            break;
          
          default:
            fixes.push({
              issue: issue.type,
              status: 'not_implemented',
              action: 'manual_fix_required'
            });
        }
      } catch (error) {
        fixes.push({
          issue: issue.type,
          status: 'error',
          error: error.message
        });
      }
    }
    
    return fixes;
  }

  async recreateConceptInNeo4j(conceptId) {
    // Получение данных из PostgreSQL
    const pgResult = await this.dbManager.postgresPool.query(
      'SELECT * FROM concepts WHERE concept_id = $1',
      [conceptId]
    );
    
    if (pgResult.rows.length === 0) {
      throw new Error(`Concept ${conceptId} not found in PostgreSQL`);
    }
    
    const conceptData = pgResult.rows[0];
    
    // Создание узла концепции в Neo4j
    const neo4jSession = this.dbManager.neo4jDriver.session();
    await neo4jSession.run(`
      CREATE (c:Concept {
        concept_id: $conceptId,
        name: $name,
        description: $description,
        creation_date: datetime($creationDate),
        innovation_degree: $innovationDegree
      })
      RETURN c
    `, {
      conceptId: conceptData.concept_id,
      name: conceptData.name,
      description: conceptData.description,
      creationDate: conceptData.creation_date.toISOString(),
      innovationDegree: conceptData.innovation_degree || 1
    });
    
    await neo4jSession.close();
  }

  async syncDataFromPostgres(conceptId, field) {
    // Получение данных из PostgreSQL
    const pgResult = await this.dbManager.postgresPool.query(
      `SELECT ${field} FROM concepts WHERE concept_id = $1`,
      [conceptId]
    );
    
    if (pgResult.rows.length === 0) {
      throw new Error(`Concept ${conceptId} not found in PostgreSQL`);
    }
    
    const value = pgResult.rows[0][field];
    
    // Обновление в Neo4j
    const neo4jSession = this.dbManager.neo4jDriver.session();
    await neo4jSession.run(`
      MATCH (c:Concept {concept_id: $conceptId})
      SET c.${field} = $value
      RETURN c
    `, {
      conceptId,
      value
    });
    
    await neo4jSession.close();
  }

  async fixCategoryType(categoryId) {
    // Получение данных категории
    const neo4jSession = this.dbManager.neo4jDriver.session();
    const result = await neo4jSession.run(
      'MATCH (cat:Category {category_id: $categoryId}) RETURN cat',
      { categoryId }
    );
    
    if (result.records.length === 0) {
      throw new Error(`Category ${categoryId} not found`);
    }
    
    const category = result.records[0].get('cat').properties;
    
    // Назначение допустимого типа категории
    const defaultType = CATEGORY_TYPES.ONTOLOGICAL;
    
    // Обновление типа категории
    await neo4jSession.run(`
      MATCH (cat:Category {category_id: $categoryId})
      SET cat.type = $type
      RETURN cat
    `, {
      categoryId,
      type: defaultType
    });
    
    await neo4jSession.close();
  }

  async fixRelationshipType(relationshipId) {
    // Получение данных отношения
    const neo4jSession = this.dbManager.neo4jDriver.session();
    const result = await neo4jSession.run(
      'MATCH ()-[r:RELATED_TO {relationship_id: $relationshipId}]->() RETURN r',
      { relationshipId }
    );
    
    if (result.records.length === 0) {
      throw new Error(`Relationship ${relationshipId} not found`);
    }
    
    // Назначение допустимого типа отношения
    const defaultType = RELATIONSHIP_TYPES.CONCEPTUAL;
    
    // Обновление типа отношения
    await neo4jSession.run(`
      MATCH ()-[r:RELATED_TO {relationship_id: $relationshipId}]->()
      SET r.type = $type
      RETURN r
    `, {
      relationshipId,
      type: defaultType
    });
    
    await neo4jSession.close();
  }

  async fixRelationshipDirection(relationshipId) {
    // Получение данных отношения
    const neo4jSession = this.dbManager.neo4jDriver.session();
    
    // Назначение допустимого направления отношения
    const defaultDirection = RELATIONSHIP_DIRECTIONS.BIDIRECTIONAL;
    
    // Обновление направления отношения
    await neo4jSession.run(`
      MATCH ()-[r:RELATED_TO {relationship_id: $relationshipId}]->()
      SET r.direction = $direction
      RETURN r
    `, {
      relationshipId,
      direction: defaultDirection
    });
    
    await neo4jSession.close();
  }

  async fixThesisType(thesisId) {
    // Назначение допустимого типа тезиса
    const defaultType = THESIS_TYPES.GENERAL;
    
    // Обновление типа тезиса
    await this.dbManager.mongodb.collection('theses').updateOne(
      { _id: thesisId },
      { $set: { type: defaultType, updated_at: new Date() } }
    );
  }

  async fixThesisStyle(thesisId) {
    // Назначение допустимого стиля тезиса
    const defaultStyle = THESIS_STYLES.ACADEMIC;
    
    // Обновление стиля тезиса
    await this.dbManager.mongodb.collection('theses').updateOne(
      { _id: thesisId },
      { $set: { style: defaultStyle, updated_at: new Date() } }
    );
  }

  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      totalConcepts: this.validationResults.length,
      validConcepts: this.validationResults.filter(r => r.status === 'valid').length,
      conceptsWithIssues: this.validationResults.filter(r => r.status === 'issues_found').length,
      errors: this.validationResults.filter(r => r.status === 'error').length,
      issuesByType: {},
      issuesBySeverity: {},
      detailedResults: this.validationResults
    };
    
    // Подсчет проблем по типам
    this.validationResults.forEach(result => {
      if (result.issues) {
        result.issues.forEach(issue => {
          report.issuesByType[issue.type] = 
            (report.issuesByType[issue.type] || 0) + 1;
          report.issuesBySeverity[issue.severity] = 
            (report.issuesBySeverity[issue.severity] || 0) + 1;
        });
      }
    });
    
    return report;
  }

  async saveReportToFile(report, filename) {
    const fs = require('fs').promises;
    await fs.writeFile(filename, JSON.stringify(report, null, 2));
    console.log(`Validation report saved to ${filename}`);
  }
}

module.exports = DataIntegrityValidator;
